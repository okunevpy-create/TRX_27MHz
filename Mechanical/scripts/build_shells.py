# -*- coding: utf-8 -*-
"""
build_shells.py — СКОРЛУПЫ корпуса (верхняя и нижняя) — этап 4.

Верхняя скорлупа = верхняя крышка + верхние половины левой/правой боковин.
Нижняя  скорлупа = дно + нижние половины боковин.
Соединение с передней панелью — язычки в пазы корытца.
Соединение скорлуп между собой — шип/паз по шву Z=25 (без винтов).
Внешняя галтель R2.5 — только рёбра «крышка <-> боковина».
Вентиляционные жабры — в боковинах.
Задняя сторона закрывается отдельной задней крышкой.

Локальная/глобальная СК (совпадает с корытцем):
    x : слева направо, наружный габарит -3..183 (186)
    y : 0 — фронт панели, +Y внутрь; скорлупы 13.4..CASE_D
    z : снизу вверх, наружный габарит -3..53 (56), шов на 25

Запуск:  freecadcmd Mechanical/scripts/build_shells.py
"""

import os
import math

import fc_common as C
from fc_common import App, Part, P
from build_front_panel import panel_dims, screw_positions, rounded_rect, extrude_xz


# ---------------------------------------------------------------------------
#  Вспомогательное
# ---------------------------------------------------------------------------
def _which_z(which):
    """(z_from, z_h) наружного призма скорлупы."""
    z_top = P.CASE_H + P.T_PROTRUDE          # 53
    z_bot = -P.T_PROTRUDE                     # -3
    if which == "top":
        return P.SHELL_SEAM_Z, z_top - P.SHELL_SEAM_Z      # 25, 28
    return z_bot, P.SHELL_SEAM_Z - z_bot                   # -3, 28


def _which_cavity(which):
    """(z_from, z_h) полости (внутренний проём) скорлупы."""
    if which == "top":
        return P.SHELL_SEAM_Z, P.CASE_H - P.SHELL_SEAM_Z   # 25, 25
    return 0.0, P.SHELL_SEAM_Z                              # 0, 25


def _cover_side_edges(shape, which):
    """
    Рёбра галтели: продольные (вдоль Y) внешние рёбра «крышка <-> боковина».

    Для верхней скорлупы — верхнее левое (x=-3,z=53) и верхнее правое
    (x=183,z=53). Для нижней — нижнее левое (x=-3,z=-3) и нижнее правое.
    """
    x0 = -P.T_PROTRUDE
    x1 = P.CASE_W + P.T_PROTRUDE
    z_target = (P.CASE_H + P.T_PROTRUDE) if which == "top" else (-P.T_PROTRUDE)
    sel = []
    for e in shape.Edges:
        v = e.tangentAt(e.FirstParameter)
        if abs(v.x) < 1e-6 and abs(v.z) < 1e-6 and abs(v.y) > 1e-6:
            p = e.valueAt(e.FirstParameter)
            if (abs(p.z - z_target) < 1e-3
                    and (abs(p.x - x0) < 1e-3 or abs(p.x - x1) < 1e-3)):
                sel.append(e)
    return sel


def _fillet(shell, which):
    """Внешняя галтель R2.5 по рёбрам «крышка <-> боковина»."""
    r = P.SHELL_FILLET
    if r <= 0:
        return shell
    edges = _cover_side_edges(shell, which)
    print("       рёбер «крышка <-> боковина»: %d" % len(edges))
    if len(edges) != 2:
        print("       [WARN] ожидалось 2 ребра — галтель пропущена")
        return shell
    trial = shell.makeFillet(r, edges)
    if trial.isValid() and len(trial.Solids) == 1:
        return trial.removeSplitter()
    print("       [WARN] makeFillet не дал валидное тело — галтель пропущена")
    return shell


def _bop_status(shape):
    """BOP-проверка: CLEAN, если check(True) вернул None/True."""
    try:
        res = shape.check(True)
    except Exception as exc:                            # noqa: BLE001
        return "ERROR: %r" % (exc,)
    if res is None or res is True:
        return "CLEAN"
    return "FAIL: %r" % (res,)


# ---------------------------------------------------------------------------
#  Тело скорлупы
# ---------------------------------------------------------------------------
def shell_solid(which):
    """Наружный призма (острые углы) -> галтель -> вырез полости."""
    x0 = -P.T_PROTRUDE
    length = P.CASE_W + 2 * P.T_PROTRUDE
    y_from = P.T_PANEL + P.BASIN_DEPTH
    y_len = P.CASE_D - y_from

    z_from, z_h = _which_z(which)
    outer = extrude_xz(rounded_rect(x0, z_from, length, z_h, 0.0), y_from, y_len)

    # Галтель ДО выреза полости (по простому призма — иначе makeFillet ломается).
    outer = _fillet(outer, which)

    cz_from, cz_h = _which_cavity(which)
    cavity = extrude_xz(rounded_rect(0.0, cz_from, P.CASE_W, cz_h, P.CORNER_R),
                        y_from, y_len)
    return outer.cut(cavity)


# ---------------------------------------------------------------------------
#  Язычки в пазы передней панели
# ---------------------------------------------------------------------------
def front_tongues(which):
    """Язычки на переднем торце + отверстия под винты + зенковки."""
    x0, z0, length, height = panel_dims()
    y_from = P.T_PANEL + P.GROOVE_FLOOR_GAP        # 2.6
    gl = P.GROOVE_L                                # 11 (чуть заходит в скорлупу)
    gw = P.GROOVE_W                                # 11
    gh = P.GROOVE_H                                # 1.5

    screw_r = P.JOIN_SCREW_D / 2.0
    csk_d = P.JOIN_SCREW_CSK_DEPTH
    csk_r_big = P.SCREW_HEAD_D / 2.0               # у поверхности (снаружи)
    csk_r_small = P.JOIN_SCREW_D / 2.0             # у дна зенковки

    adds, cuts = [], []
    for name, ca, y_c, axis in screw_positions():
        if axis == "Z":
            own = (which == "top") if name.startswith("top") else (which == "bottom")
        else:
            own = (which == "top") if (ca >= P.SHELL_SEAM_Z) else (which == "bottom")
        if not own:
            continue

        if axis == "Z":
            z_from = (z0 + height - gh) if name.startswith("top") else z0
            adds.append(C.box(ca - gw / 2.0, y_from, z_from, gw, gl, gh))
            # сквозное отверстие под винт (ось Z)
            cuts.append(C.cyl_z(ca, y_c, z_from, screw_r, gh))
            # зенковка: большим диаметром к наружной грани
            if name.startswith("top"):
                cuts.append(C.cone_z(ca, y_c, z_from + gh - csk_d,
                                     csk_r_small, csk_r_big, csk_d))
            else:
                cuts.append(C.cone_z(ca, y_c, z0, csk_r_big, csk_r_small, csk_d))
        else:
            x_from = x0 if name.startswith("left") else (x0 + length - gh)
            adds.append(C.box(x_from, y_from, ca - gw / 2.0, gh, gl, gw))
            # сквозное отверстие под винт (ось X)
            cuts.append(C.cyl_x(y_c, ca, x_from, screw_r, gh))
            # зенковка: большим диаметром к наружной грани
            if name.startswith("left"):
                cuts.append(C.cone_x(y_c, ca, x0, csk_r_big, csk_r_small, csk_d))
            else:
                cuts.append(C.cone_x(y_c, ca, x_from + gh - csk_d,
                                     csk_r_small, csk_r_big, csk_d))
    return adds, cuts


# ---------------------------------------------------------------------------
#  Шов скорлуп (шип/паз по боковинам, весь Y, без винтов)
# ---------------------------------------------------------------------------
def seam_feature(which):
    """
    Шов скорлуп — «1 язычок + 1 паз» на каждой скорлупе (без винтов).

    Верхняя: язычок ВНИЗ на левой боковине + паз ВВЕРХ на правой.
    Нижняя : паз ВНИЗ на левой боковине + язычок ВВЕРХ на правой.
    Так язычок одной скорлупы входит в паз другой, и наоборот.
    """
    y_from = P.T_PANEL + P.BASIN_DEPTH
    y_len = P.CASE_D - y_from
    zh = P.SEAM_TONGUE_H
    tt = P.SEAM_TONGUE_T
    c = P.SEAM_CLEAR
    seam = P.SHELL_SEAM_Z

    adds, cuts = [], []
    if which == "top":
        # Левый язычок вниз + правый паз вверх.
        adds.append(C.box(-tt, y_from, seam - zh, tt, y_len, zh))
        cuts.append(C.box(P.CASE_W, y_from, seam, tt + c, y_len, zh + c))
    else:
        # Левый паз вниз + правый язычок вверх.
        cuts.append(C.box(-tt - c, y_from, seam - zh - c, tt + c, y_len, zh + c))
        adds.append(C.box(P.CASE_W, y_from, seam, tt, y_len, zh))
    return adds, cuts


def rear_join_feature(which):
    """
    Заднее соединение — 8 пазов (топ/низ/лево/право), зеркально передней панели.

    Верхняя скорлупа: 2 паза сверху + 2 боковых (лево/право) выше шва.
    Нижняя  скорлупа: 2 паза снизу + 2 боковых (лево/право) ниже шва.
    Каждый паз: паз + отверстие под винт + бобышка под гайку (как у передней).
    """
    x0, z0, length, height = panel_dims()
    gw = P.GROOVE_W + P.GROOVE_CLEAR
    gh = P.GROOVE_H
    gl = P.GROOVE_L
    y_out = P.CASE_D                                # 160 — задний торец
    y_start = y_out - gl + P.GROOVE_FLOOR_GAP       # 149.2
    y_center = y_out - gl / 2.0                     # 154.5 — центр паза

    adds, cuts = [], []

    for name, ca, _y, axis in screw_positions(y_c=y_center):
        if axis == "Z":
            own = (which == "top") if name.startswith("top") else (which == "bottom")
        else:
            own = (which == "top") if (ca >= P.SHELL_SEAM_Z) else (which == "bottom")
        if not own:
            continue

        if axis == "Z":
            z_face = (z0 + height - gh) if name.startswith("top") else z0
            # паз (вырез наружной 1.5 мм стенки)
            cuts.append(C.box(ca - gw / 2.0, y_start, z_face, gw, gl + 0.02, gh + 0.01))
            # отверстие под винт
            cuts.append(C.cyl_z(ca, y_center, z_face, P.JOIN_SCREW_D / 2.0, gh))
            # бобышка под гайку на внутренней стороне стенки
            z_b = (z_face - P.NUT_BOSS_H) if name.startswith("top") else (z_face + gh)
            adds.append(C.cyl_z(ca, y_center, z_b, P.NUT_BOSS_D / 2.0, P.NUT_BOSS_H))
            cuts.append(C.cyl_z(ca, y_center, z_b, P.NUT_BOSS_HOLE_D / 2.0, P.NUT_BOSS_H))
        else:
            x_from = x0 if name.startswith("left") else (x0 + length - gh)
            # паз (вырез наружной 1.5 мм боковой стенки)
            cuts.append(C.box(x_from, y_start, ca - gw / 2.0, gh + 0.01, gl + 0.02, gw))
            # отверстие под винт
            cuts.append(C.cyl_x(y_center, ca, x_from, P.JOIN_SCREW_D / 2.0, gh))
            # бобышка под гайку на внутренней стороне стенки
            x_b = (x_from + gh) if name.startswith("left") else (x_from - P.NUT_BOSS_H)
            adds.append(C.cyl_x(y_center, ca, x_b, P.NUT_BOSS_D / 2.0, P.NUT_BOSS_H))
            cuts.append(C.cyl_x(y_center, ca, x_b, P.NUT_BOSS_HOLE_D / 2.0, P.NUT_BOSS_H))

    return adds, cuts


# ---------------------------------------------------------------------------
#  Вентиляционные жабры в боковинах
# ---------------------------------------------------------------------------
def vent_cuts(which):
    y_from = P.T_PANEL + P.BASIN_DEPTH
    y_len = P.CASE_D - y_from
    cy = y_from + y_len / 2.0

    z_from, z_h = _which_z(which)
    cz = z_from + z_h / 2.0
    span_z = z_h - 2 * P.VENT_MARGIN_Z
    span_y = y_len - 2 * P.VENT_MARGIN_Y

    tools = []
    tools += C.vent_slots_x(-P.T_PROTRUDE - 0.5, 0.5,
                            cy, cz, span_y, span_z)
    tools += C.vent_slots_x(P.CASE_W - 0.5, P.CASE_W + P.T_PROTRUDE + 0.5,
                            cy, cz, span_y, span_z)
    return tools


# ---------------------------------------------------------------------------
#  Стойки под платы (на дне нижней скорлупы)
# ---------------------------------------------------------------------------
def board1_mount_features():
    """Стойки под плату 01_control: бобышки Ø8 + пилот под самонарез M3.

    Координаты стоек — из params.board1_hole_positions() (4 монтажных
    отверстия H1..H4 платы). Стойки растут от дна (z=0) вверх.
    """
    adds = []
    for _name, hx, hy in P.board1_hole_positions():
        adds.append(C.boss(hx, hy, 0.0,
                           d=P.BOARD1_STANDOFF_D,
                           hole_d=P.BOARD1_STANDOFF_HOLE_D,
                           h=P.BOARD1_STANDOFF_H))
    return adds


def board2_mount_features():
    """Стойки под плату 02_power_amp: бобышки Ø8 + пилот под самонарез M3.

    Координаты стоек — из params.board2_hole_positions() (4 монтажных
    отверстия H1..H4 платы). Стойки растут от дна (z=0) вверх.
    """
    adds = []
    for _name, hx, hy in P.board2_hole_positions():
        adds.append(C.boss(hx, hy, 0.0,
                           d=P.BOARD2_STANDOFF_D,
                           hole_d=P.BOARD2_STANDOFF_HOLE_D,
                           h=P.BOARD2_STANDOFF_H))
    return adds


# ---------------------------------------------------------------------------
#  Сборка
# ---------------------------------------------------------------------------
def build(which):
    print("[1/5] Корпус скорлупы (%s)" % which)
    body = shell_solid(which)
    C.report(body, "скорлупа (%s) — заготовка" % which)

    print("[2/5] Язычки + винты в переднюю панель")
    ta, tc = front_tongues(which)
    body = C.fuse(body, *ta)
    body = C.cut(body, *tc)

    print("[3/5] Шов скорлуп (шип/паз)")
    sa, sc = seam_feature(which)
    body = C.fuse(body, *sa)
    body = C.cut(body, *sc)

    print("[4/5] Задние пазы/бобышки под крышку")
    ra, rc = rear_join_feature(which)
    body = C.fuse(body, *ra)
    body = C.cut(body, *rc)

    print("[5/5] Вентиляционные жабры")
    body = C.cut(body, *vent_cuts(which))

    if which == "bottom":
        print("[6/7] Стойки под плату 01_control")
        body = C.fuse(body, *board1_mount_features())
        print("[7/7] Стойки под плату 02_power_amp")
        body = C.fuse(body, *board2_mount_features())

    return body.removeSplitter()


def run():
    problems = P.sanity_check()
    if problems:
        print("[ERR] params.py:")
        for x in problems:
            print("      -", x)
        return 2

    for which in ("bottom", "top"):
        doc = C.new_doc("shell_" + which)
        body = build(which)
        C.report(body, "СКОРЛУПА (%s)" % which)
        print("       BOP check : %s" % _bop_status(body))

        C.add_shape(doc, body, "Shell_" + which,
                    "Скорлупа (%s)" % which)
        print("[OK] FCStd :", C.save_fcstd(doc, "shell_%s.FCStd" % which))
        for k, v in C.export_all(doc, body, "shell_" + which).items():
            print("[OK] %-4s : %s" % (k.upper(), v))
    print("[DONE] shells")
    return 0


def _is_main():
    """Определить, запущен ли скрипт напрямую через freecadcmd."""
    import sys
    if __name__ == "__main__":
        return True
    here = os.path.basename(__file__)
    return any(os.path.basename(a) == here for a in sys.argv[1:])


if _is_main():
    import sys
    sys.exit(run())
