# -*- coding: utf-8 -*-
"""
build_front_panel.py — ПЕРЕДНЯЯ ПАНЕЛЬ-КОРЫТЦЕ корпуса TRX-27MHz (этап 4).

Деталь — корытце: фронтальная плита + стенки по контуру глубиной
BASIN_DEPTH. Соединение с дном, верхней крышкой и боковинами — паз
(выемка со стороны полости) + язычок детали.

Локальная СК детали:
    x : слева направо
    y : 0 — наружная плоскость фронта, +Y — внутрь корпуса
    z : снизу вверх

ВАЖНО (FreeCAD 26.3 / OCC):
    Наружная галтель наносится НА ПРОСТУЮ ПРИЗМУ ДО выреза полости и
    прочих элементов. В таком порядке makeFillet даёт корректную модель,
    STEP пишется чисто (без InvalidCurveOnSurface, BOP check CLEAN).
    makeFillet по телу с вырезами даёт дефекты — порядок операций важен.

Запуск:  freecadcmd Mechanical/scripts/build_front_panel.py
"""

import math
import os

import fc_common as C
from fc_common import App, Part, P


# ---------------------------------------------------------------------------
#  Габарит и 2D-контуры
# ---------------------------------------------------------------------------
def panel_dims():
    """x0, z0, длина, высота наружной плиты (с учётом выступа T_PROTRUDE)."""
    x0 = -P.T_PROTRUDE
    z0 = -P.T_PROTRUDE
    length = P.CASE_W + 2 * P.T_PROTRUDE
    height = P.CASE_H + 2 * P.T_PROTRUDE
    return x0, z0, length, height


def _arc_pts(cx, cz, r, a0_deg, a1_deg, steps=16):
    """Точки дуги от a0 до a1 (градусы), не включая первую."""
    n = max(1, int(steps * abs(a1_deg - a0_deg) / 90.0))
    out = []
    for i in range(n + 1):
        t = math.radians(a0_deg + (a1_deg - a0_deg) * i / n)
        out.append((cx + r * math.cos(t), cz + r * math.sin(t)))
    return out


def _face_from_pts(pts):
    """Замкнутая грань в плоскости XZ по списку точек (x, z)."""
    pts = list(pts)
    if abs(pts[0][0] - pts[-1][0]) > 1e-9 or abs(pts[0][1] - pts[-1][1]) > 1e-9:
        pts.append(pts[0])
    w = [App.Vector(x, 0.0, z) for (x, z) in pts]
    return Part.Face(Part.makePolygon(w, True))


def rounded_rect(x0, z0, length, height, radius, steps=16):
    """
    Прямоугольник со скруглёнными углами — грань в плоскости XZ.

    Углы — НАСТОЯЩИЕ дуги (Part.Arc), а не полилиния из фасеток.
    Это важно: на фасеточном контуре makeFillet по кромке не работает
    (кромка разбита на сотни кусочков по 0.25 мм).
    """
    r = max(0.0, min(radius, length / 2.0 - 1e-3, height / 2.0 - 1e-3))
    x1, z1 = x0 + length, z0 + height
    if r <= 1e-9:
        return _face_from_pts([(x0, z0), (x1, z0), (x1, z1), (x0, z1)])

    def ln(a, b):
        return Part.makeLine(App.Vector(a[0], 0, a[1]),
                             App.Vector(b[0], 0, b[1]))

    def arc(cx, cz, a0, a1):
        A = App.Vector(cx + r * math.cos(math.radians(a0)), 0,
                       cz + r * math.sin(math.radians(a0)))
        B = App.Vector(cx + r * math.cos(math.radians((a0 + a1) / 2.0)), 0,
                       cz + r * math.sin(math.radians((a0 + a1) / 2.0)))
        Cc = App.Vector(cx + r * math.cos(math.radians(a1)), 0,
                        cz + r * math.sin(math.radians(a1)))
        return Part.Arc(A, B, Cc).toShape()

    edges = [
        ln((x1 - r, z0), (x0 + r, z0)),        # низ
        arc(x0 + r, z0 + r, 270, 180),         # BL
        ln((x0, z0 + r), (x0, z1 - r)),        # лево
        arc(x0 + r, z1 - r, 180, 90),          # TL
        ln((x0 + r, z1), (x1 - r, z1)),        # верх
        arc(x1 - r, z1 - r, 90, 0),            # TR
        ln((x1, z1 - r), (x1, z0 + r)),        # право
        arc(x1 - r, z0 + r, 0, -90),           # BR
    ]
    return Part.Face(Part.Wire(edges))


def extrude_xz(face, y_from, depth):
    """Выдавить грань из плоскости XZ вдоль +Y."""
    solid = face.extrude(App.Vector(0, depth, 0))
    if abs(y_from) > 1e-12:
        solid.translate(App.Vector(0, y_from, 0))
    return solid


# ---------------------------------------------------------------------------
#  Наружная галтель
# ---------------------------------------------------------------------------
def _front_perimeter_edges(shape, y=0.0, tol=1e-4):
    """
    Рёбра простого тела, целиком лежащие в плоскости y = const.

    Для призматического тела это в точности периметр лицевой стороны
    (4 прямых + 4 дуги углов). Вертикальные рёбра стенок (вдоль Y) сюда
    не попадают: у них середина на y != 0.
    """
    sel = []
    for e in shape.Edges:
        try:
            a, b = e.FirstParameter, e.LastParameter
            pts = (e.valueAt(a), e.valueAt(b), e.valueAt((a + b) / 2.0))
        except Exception:
            continue
        if all(abs(p.y - y) <= tol for p in pts):
            sel.append(e)
    return sel


def outer_fillet(body):
    """
    Наружная галтель по периметру лицевой стороны (y=0): кромка
    «фронтальная плита -> стенки».

    НАНОСИТСЯ НА ПРОСТУЮ ПРИЗМУ ДО выреза полости — makeFillet по телу
    с вырезами даёт дефекты (потеря объёма, «пропавшие» отверстия).
    """
    r = P.OUTER_FILLET
    if r <= 0:
        return body
    edges = _front_perimeter_edges(body)
    print("       рёбер периметра лицевой стороны: %d" % len(edges))
    if not edges:
        print("       [WARN] рёбра лицевой стороны не найдены — галтель пропущена")
        return body
    trial = body.makeFillet(r, edges)
    if trial.isValid() and len(trial.Solids) == 1:
        return trial.removeSplitter()
    print("       [WARN] makeFillet не дал валидное тело — галтель пропущена")
    return body


# ---------------------------------------------------------------------------
#  Корпус корытца
# ---------------------------------------------------------------------------
def basin_body():
    """Плита + стенки по периметру + наружная галтель (наносится ДО выреза полости)."""
    x0, z0, length, height = panel_dims()
    tw = P.BASIN_WALL
    y_end = P.T_PANEL + P.BASIN_DEPTH

    outer = extrude_xz(rounded_rect(x0, z0, length, height, P.CORNER_R),
                       0.0, y_end)

    # Галтель — на простую призму, до выреза полости (иначе makeFillet ломается).
    outer = outer_fillet(outer)

    # углы полости уменьшены на толщину стенки — стенка равномерна по контуру
    inner_r = max(P.CORNER_R - tw, 0.5)
    inner_pol = rounded_rect(x0 + tw, z0 + tw, length - 2 * tw,
                             height - 2 * tw, inner_r)
    cavity = extrude_xz(inner_pol, P.T_PANEL, P.BASIN_DEPTH + 1.0)

    return outer.cut(cavity), None


def inner_rim_fillet(body):
    """Скругление внутренней кромки «пол корытца -> стенка»."""
    r = P.BASIN_FILLET
    if r <= 0:
        return body
    x0, z0, length, height = panel_dims()
    tw = P.BASIN_WALL
    y_floor = P.T_PANEL
    tol = 1e-3
    xi0, xi1 = x0 + tw, x0 + length - tw
    zi0, zi1 = z0 + tw, z0 + height - tw

    cand = []
    for e in body.Edges:
        p = e.valueAt(e.FirstParameter)
        if abs(p.y - y_floor) > tol:
            continue
        v = e.tangentAt(e.FirstParameter)
        if abs(v.y) < 1e-6 and abs(v.z) < 1e-6 and abs(v.x) > 1e-6:
            if abs(p.z - zi0) < tol or abs(p.z - zi1) < tol:
                cand.append(e)
        elif abs(v.x) < 1e-6 and abs(v.y) < 1e-6 and abs(v.z) > 1e-6:
            if abs(p.x - xi0) < tol or abs(p.x - xi1) < tol:
                cand.append(e)

    print("       рёбер «пол->стенка»: %d" % len(cand))
    if not cand:
        return body
    try:
        trial = body.makeFillet(r, cand)
        if trial.isValid() and len(trial.Solids) == 1:
            print("       скруглено внутр.: %d" % len(cand))
            return trial
    except Exception:                                  # noqa: BLE001
        pass
    print("       [WARN] внутреннее скругление не выполнено")
    return body


# ---------------------------------------------------------------------------
#  Пазы, бобышки, крепёж
# ---------------------------------------------------------------------------
def screw_positions():
    """[(name, ca, cb, axis)] — оси саморезов, по центру пазов."""
    x0, z0, length, height = panel_dims()
    y_c = (P.T_PANEL + P.BASIN_DEPTH) - P.GROOVE_L / 2.0
    pos = []
    for i in range(P.JOIN_SCREWS_TOP):
        f = (i + 1.0) / (P.JOIN_SCREWS_TOP + 1.0)
        pos.append(("top%d" % (i + 1), x0 + f * length, y_c, "Z"))
    for i in range(P.JOIN_SCREWS_BOTTOM):
        f = (i + 1.0) / (P.JOIN_SCREWS_BOTTOM + 1.0)
        pos.append(("bot%d" % (i + 1), x0 + f * length, y_c, "Z"))
    for i in range(P.JOIN_SCREWS_LEFT):
        f = (i + 1.0) / (P.JOIN_SCREWS_LEFT + 1.0)
        pos.append(("left%d" % (i + 1), z0 + f * height, y_c, "X"))
    for i in range(P.JOIN_SCREWS_RIGHT):
        f = (i + 1.0) / (P.JOIN_SCREWS_RIGHT + 1.0)
        pos.append(("right%d" % (i + 1), z0 + f * height, y_c, "X"))
    return pos


def groove_cuts():
    """Паз: вырез со стороны полости, GROOVE_W x GROOVE_L x GROOVE_H."""
    x0, z0, length, height = panel_dims()
    gw = P.GROOVE_W + P.GROOVE_CLEAR
    gh = P.GROOVE_H
    gl = P.GROOVE_L
    y_out = P.T_PANEL + P.BASIN_DEPTH
    y_start = y_out - gl + P.GROOVE_FLOOR_GAP
    cuts = []

    for name, ca, _y, axis in screw_positions():
        if axis == "Z":
            z_from = (z0 + height - gh) if name.startswith("top") else z0
            cuts.append(C.box(ca - gw / 2.0, y_start, z_from,
                              gw, gl + 0.02, gh + 0.01))
        else:
            x_from = x0 if name.startswith("left") else (x0 + length - gh)
            cuts.append(C.box(x_from, y_start, ca - gw / 2.0,
                              gh + 0.01, gl + 0.02, gw))
    return cuts


def nut_bosses():
    """
    Бобышки под закладные гайки M3 — на ВНУТРЕННЕЙ стороне стенки.

    ПРАВИЛО: бобышка стоит ЗА пазом. Паз снимает от торца слой GROOVE_H,
    значит рабочая плоскость стенки — на глубине GROOVE_H от торца.
    Бобышка начинается РОВНО на этой плоскости и растёт в полость.
    В паз не заходит ни на миллиметр.

    Карман под гайку — СКВОЗНОЙ насквозь бобышки в полость. Гайка
    вставляется со стороны полости, винт идёт из паза. Никакого «дна»
    кармана нет — иначе отверстие получается глухим.
    """
    x0, z0, length, height = panel_dims()
    gh = P.GROOVE_H
    bh = P.NUT_BOSS_H
    adds, cuts = [], []

    for name, ca, y_c, axis in screw_positions():
        if axis == "Z":
            if name.startswith("top"):
                face = z0 + height - gh           # рабочая плоскость
                z_b = face - bh                   # бобышка вниз, в полость
                adds.append(C.cyl_z(ca, y_c, z_b, P.NUT_BOSS_D / 2.0, bh))
                # карман сквозной ровно в пределах бобышки
                cuts.append(C.cyl_z(ca, y_c, z_b,
                                    P.NUT_BOSS_HOLE_D / 2.0, bh))
            else:
                face = z0 + gh
                adds.append(C.cyl_z(ca, y_c, face, P.NUT_BOSS_D / 2.0, bh))
                cuts.append(C.cyl_z(ca, y_c, face,
                                    P.NUT_BOSS_HOLE_D / 2.0, bh))
        else:
            if name.startswith("left"):
                face = x0 + gh
                adds.append(C.cyl_x(y_c, ca, face, P.NUT_BOSS_D / 2.0, bh))
                cuts.append(C.cyl_x(y_c, ca, face,
                                    P.NUT_BOSS_HOLE_D / 2.0, bh))
            else:
                face = x0 + length - gh
                x_b = face - bh
                adds.append(C.cyl_x(y_c, ca, x_b, P.NUT_BOSS_D / 2.0, bh))
                cuts.append(C.cyl_x(y_c, ca, x_b,
                                    P.NUT_BOSS_HOLE_D / 2.0, bh))
    return adds, cuts


def screw_holes():
    """
    Отверстие под саморез M3 — сквозное через остаток стенки, по оси паза.

    Идёт от плоскости торца (за пазом — там пусто) через материал стенки
    до кармана гайки. Сверлим от дна паза до торца с запасом.

    Отверстие НЕ выходит за пределы стенки по Y: ось совпадает с осью
    паза, а паз занимает всю глубину корытца — поэтому по Y всё в габарите.
    """
    x0, z0, length, height = panel_dims()
    gh = P.GROOVE_H
    depth = gh                         # ровно остаток стенки
    cuts = []

    for name, ca, y_c, axis in screw_positions():
        if axis == "Z":
            if name.startswith("top"):
                z_from = z0 + height - gh
                cuts.append(C.cyl_z(ca, y_c, z_from,
                                    P.JOIN_SCREW_D / 2.0, depth))
            else:
                z_from = z0
                cuts.append(C.cyl_z(ca, y_c, z_from,
                                    P.JOIN_SCREW_D / 2.0, depth))
        else:
            if name.startswith("left"):
                cuts.append(C.cyl_x(y_c, ca, x0,
                                    P.JOIN_SCREW_D / 2.0, depth))
            else:
                x_from = x0 + length - gh
                cuts.append(C.cyl_x(y_c, ca, x_from,
                                    P.JOIN_SCREW_D / 2.0, depth))
    return cuts


# ---------------------------------------------------------------------------
#  Элементы на фронтальной плите
# ---------------------------------------------------------------------------
def screen_features():
    cx, cz = P.SCR_CENTER_X, P.SCR_CENTER_Z
    y_in = P.T_PANEL
    cuts, adds = [], []

    cuts.append(C.box(cx - P.SCR_WINDOW_W / 2.0, -1.0,
                      cz - P.SCR_WINDOW_H / 2.0,
                      P.SCR_WINDOW_W, P.T_PANEL + 2.0, P.SCR_WINDOW_H))
    niche_d = P.SCR_PCB_GAP
    cuts.append(C.box(cx - P.SCR_BODY_W / 2.0, y_in - niche_d,
                      cz - P.SCR_BODY_H / 2.0,
                      P.SCR_BODY_W, niche_d + 1.0, P.SCR_BODY_H))

    dx, dz = P.SCR_HOLE_DX / 2.0, P.SCR_HOLE_DY / 2.0
    for sx in (-1, 1):
        for sz in (-1, 1):
            adds.append(C.cyl_y(cx + sx * dx, cz + sz * dz, y_in,
                                P.SCR_STANDOFF_D / 2.0, P.SCR_STANDOFF_H))
            cuts.append(C.cyl_y(cx + sx * dx, cz + sz * dz, y_in - 0.5,
                                P.SCR_STANDOFF_HOLE_D / 2.0,
                                P.SCR_STANDOFF_H + 1.0))
    return cuts, adds


def encoder_features():
    cx, cz = P.ENC_CENTER_X, P.ENC_CENTER_Z
    y_in = P.T_PANEL
    cuts, adds = [], []

    cuts.append(C.cyl_y(cx, cz, -1.0, P.ENC_BUSHING_D / 2.0, P.T_PANEL + 2.0))
    nut_r = (P.ENC_NUT_FLAT / 2.0) * 1.155
    cuts.append(C.cyl_y(cx, cz, -P.ENC_NUT_DEPTH, nut_r, P.ENC_NUT_DEPTH + 0.02))

    dx, dz = P.ENC_HOLES_DX / 2.0, P.ENC_HOLES_DZ / 2.0
    zs = (-dz, dz) if dz > 1e-9 else (0.0,)
    for sx in (-1.0, 1.0):
        for sz_off in zs:
            px, pz = cx + sx * dx, cz + sz_off
            adds.append(C.cyl_y(px, pz, y_in, P.ENC_STANDOFF_D / 2.0,
                                P.ENC_STANDOFF_H))
            cuts.append(C.cyl_y(px, pz, y_in - 0.5, P.ENC_SCREW_HOLE_D / 2.0,
                                P.ENC_STANDOFF_H + 1.0))
    return cuts, adds


def joystick_features():
    cx, cz = P.JOY_CENTER_X, P.JOY_CENTER_Z
    y_in = P.T_PANEL
    cuts, adds = [], []

    cuts.append(C.cyl_y(cx, cz, -1.0, P.JOY_SHAFT_HOLE_D / 2.0, P.T_PANEL + 2.0))
    dx, dz = P.JOY_SCREW_DX / 2.0, P.JOY_SCREW_DY / 2.0
    boss_d = P.BOSS_D * 0.75
    for sx in (-1, 1):
        for sz in (-1, 1):
            px, pz = cx + sx * dx, cz + sz * dz
            adds.append(C.cyl_y(px, pz, y_in, boss_d / 2.0, P.JOY_STANDOFF_H))
            cuts.append(C.cyl_y(px, pz, y_in - 0.5, P.JOY_SCREW_HOLE_D / 2.0,
                                P.JOY_STANDOFF_H + 1.0))
    return cuts, adds


def headset_features():
    """
    Гарнитура 3.5 / 2.5 мм.

    Сквозное отверстие в плите + цековка под буртик снаружи + усиливающий
    буртик с ТЫЛЬНОЙ стороны.

    ВАЖНО: усиливающий буртик — это КОЛЬЦО, а не сплошной цилиндр. Иначе он
    закрывает срез сквозного отверстия и гнездо не вставить.
    """
    if not P.HS_ENABLED:
        return [], []
    y_in = P.T_PANEL
    cuts, adds = [], []

    for cz, hole_d, bezel_d, seal_d in (
            (P.HS_35_CENTER_Z, P.HS_35_HOLE_D, P.HS_35_BEZEL_D, P.HS_SEAL_D),
            (P.HS_25_CENTER_Z, P.HS_25_HOLE_D, P.HS_25_BEZEL_D, P.HS_SEAL_D_25)):
        cx = P.HS_CENTER_X
        # сквозное отверстие — насквозь плиты с запасом
        cuts.append(C.cyl_y(cx, cz, -1.0, hole_d / 2.0, P.T_PANEL + 2.0))
        # цековка под буртик гнезда — снаружи
        cuts.append(C.cyl_y(cx, cz, -P.HS_BEZEL_DEPTH, bezel_d / 2.0,
                            P.HS_BEZEL_DEPTH + 0.02))
        # усиливающее КОЛЬЦО с тыльной стороны = цилиндр минус отверстие
        ring = C.cyl_y(cx, cz, y_in, seal_d / 2.0, P.HS_SEAL_H)
        ring = ring.cut(C.cyl_y(cx, cz, y_in - 0.5, hole_d / 2.0,
                                P.HS_SEAL_H + 1.0))
        adds.append(ring)
    return cuts, adds


def led_features():
    if not P.LED_ENABLED:
        return [], []
    cuts = []
    for _n, cx, cz in P.led_positions():
        cuts.append(C.cyl_y(cx, cz, -1.0, P.LED_HOLE_D / 2.0, P.T_PANEL + 2.0))
        cuts.append(C.cyl_y(cx, cz, -P.LED_BEZEL_DEPTH, P.LED_BEZEL_D / 2.0,
                            P.LED_BEZEL_DEPTH + 0.02))
    return cuts, []


def rit_features():
    if not P.RIT_ENABLED:
        return [], []
    cx, cz = P.RIT_CENTER_X, P.RIT_CENTER_Z
    return [
        C.cyl_y(cx, cz, -1.0, P.RIT_HOLE_D / 2.0, P.T_PANEL + 2.0),
        C.cyl_y(cx, cz, -P.RIT_BEZEL_DEPTH, P.RIT_BEZEL_D / 2.0,
                P.RIT_BEZEL_DEPTH + 0.02),
    ], []


def toggle_features():
    """Тумблер питания KN3(B)-101A-A1: сквозное отверстие + цековка под гайку."""
    if not P.PWR_SW_ENABLED:
        return [], []
    cx, cz = P.PWR_SW_CENTER_X, P.PWR_SW_CENTER_Z
    return [
        C.cyl_y(cx, cz, -1.0, P.PWR_SW_HOLE_D / 2.0, P.T_PANEL + 2.0),
        C.cyl_y(cx, cz, -P.PWR_SW_BEZEL_DEPTH, P.PWR_SW_BEZEL_D / 2.0,
                P.PWR_SW_BEZEL_DEPTH + 0.02),
    ], []


# ---------------------------------------------------------------------------
#  Сборка
# ---------------------------------------------------------------------------
def _apply(base, adds, cuts, verbose=True):
    for a in adds:
        base = base.fuse(a)
    for c in cuts:
        base = base.cut(c)
    return base


def build():
    x0, z0, length, height = panel_dims()
    print("[1/10] Корытце: %.1f x %.1f, стенка %.1f, глубина %.1f, галтель %.1f"
          % (length, height, P.BASIN_WALL, P.BASIN_DEPTH, P.OUTER_FILLET))
    body, _ = basin_body()
    body = body.removeSplitter()
    body = inner_rim_fillet(body)
    C.report(body, "корытце (заготовка)")

    print("[2/10] Пазы: %d шт" % len(screw_positions()))
    body = _apply(body, [], groove_cuts())

    print("[3/10] Бобышки под гайки + отверстия под саморез")
    ba, bc = nut_bosses()
    body = _apply(body, ba, bc + screw_holes())

    for i, (label, fn) in enumerate((
            ("[4/10] Экран", screen_features),
            ("[5/10] Энкодер", encoder_features),
            ("[6/10] Джойстик", joystick_features),
            ("[7/10] Гарнитура", headset_features),
            ("[8/10] Светодиоды", led_features),
            ("[9/10] Кнопка RIT", rit_features),
            ("[10/10] Тумблер питания", toggle_features))):
        print(label)
        c, a = fn()
        body = _apply(body, a, c)

    body = body.removeSplitter()
    return body


def run():
    problems = P.sanity_check()
    if problems:
        print("[ERR] params.py:")
        for x in problems:
            print("      -", x)
        return 2

    doc = C.new_doc("front_panel")
    body = build()
    C.report(body, "ПЕРЕДНЯЯ ПАНЕЛЬ (корытце)")

    C.add_shape(doc, body, "FrontPanel", "Передняя панель (корытце)")
    print("[OK] FCStd :", C.save_fcstd(doc, "front_panel.FCStd"))
    for k, v in C.export_all(doc, body, "front_panel").items():
        print("[OK] %-4s : %s" % (k.upper(), v))
    print("[DONE] front_panel")
    return 0


def _is_main():
    """Определить, запущен ли скрипт напрямую через freecadcmd.

    В freecadcmd `__name__` равен basename скрипта (без .py) и при прямом
    запуске, и при импорте, поэтому стандартная проверка
    `__name__ == "__main__"` не работает, а сравнение `__name__` с basename
    ломает импорт (run() срабатывает на импорте). Надёжный признак: имя
    файла скрипта присутствует среди аргументов командной строки
    (sys.argv[1:]) — при импорте там имя вызывающего скрипта, а не этого.
    """
    import sys
    if __name__ == "__main__":
        return True
    here = os.path.basename(__file__)
    return any(os.path.basename(a) == here for a in sys.argv[1:])


if _is_main():
    import sys
    sys.exit(run())
