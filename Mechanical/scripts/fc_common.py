# -*- coding: utf-8 -*-
"""
fc_common.py — общие утилиты для скриптов генерации корпуса TRX-27MHz.

Работает и в GUI FreeCAD (Macro -> Execute), и в консоли:
    freecadcmd Mechanical/scripts/build_front_panel.py

Правила:
  * Все размеры — только из Mechanical/params.py.
  * Все файлы пишутся только внутрь Mechanical/ (enclosure/, enclosure/exports/, Temp/).
  * Экспорт API FreeCAD 26.x:
        .FCStd -> Document.saveAs(abs)
        .stl   -> MeshPart.meshFromShape(...) -> Mesh.write(abs)
        .step  -> Part.export([obj], abs)
"""

import os
import sys
import math

# --- пути проекта -----------------------------------------------------------
_HERE = os.path.dirname(os.path.abspath(__file__))
MECH_DIR = os.path.dirname(_HERE)                       # .../Mechanical
PROJ_DIR = os.path.dirname(MECH_DIR)                    # .../TRX_27MHz
ENC_DIR = os.path.join(MECH_DIR, "enclosure")
EXP_DIR = os.path.join(ENC_DIR, "exports")
TMP_DIR = os.path.join(MECH_DIR, "Temp")

for _d in (ENC_DIR, EXP_DIR, TMP_DIR):
    if not os.path.isdir(_d):
        os.makedirs(_d)

# params.py лежит в Mechanical/
if MECH_DIR not in sys.path:
    sys.path.insert(0, MECH_DIR)

import params as P  # noqa: E402


# --- импорт FreeCAD ---------------------------------------------------------
try:
    import FreeCAD as App
    import Part
    HAVE_FC = True
except ImportError:                                     # pragma: no cover
    App = None
    Part = None
    HAVE_FC = False


# ===========================================================================
#  Документ
# ===========================================================================
def new_doc(name):
    """Создать новый документ, закрыв одноимённый существующий."""
    if not HAVE_FC:
        raise RuntimeError("FreeCAD API недоступен — запускайте скрипт через freecadcmd или GUI FreeCAD")
    if name in App.listDocuments():
        App.closeDocument(name)
    return App.newDocument(name)


def add_shape(doc, shape, name, label=None):
    """Положить TopoShape в документ как Part::Feature."""
    obj = doc.addObject("Part::Feature", name)
    obj.Shape = shape
    if label:
        obj.Label = label
    return obj


# ===========================================================================
#  Экспорт
# ===========================================================================
def save_fcstd(doc, filename=None):
    path = os.path.join(ENC_DIR, filename or (doc.Name + ".FCStd"))
    doc.recompute()
    doc.saveAs(path)
    return path


def export_stl(shape, filename, linear=None, angular=None):
    import MeshPart
    lin = linear if linear is not None else P.STL_LINEAR_DEFLECTION
    ang = angular if angular is not None else P.STL_ANGULAR_DEFLECTION
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=lin,
                                  AngularDeflection=ang)
    path = os.path.join(EXP_DIR, filename)
    mesh.write(path)
    return path


def export_step(obj, filename):
    """
    Экспорт STEP.

    Важно (FreeCAD 26.x): Part.export() экспортирует ТОЛЬКО документные объекты
    (Part::Feature). Голый TopoShape он принимает молча, но НИЧЕГО не пишет
    (получается файл на пару килобайт без геометрии). Поэтому работаем либо с
    документным объектом, либо через Shape.exportStep() напрямую.
    """
    path = os.path.join(EXP_DIR, filename)
    has_shape = hasattr(obj, "Shape")
    if not has_shape:
        # obj — TopoShape: экспортируем напрямую, минуя Part.export
        obj.exportStep(path)
        return path
    import tempfile
    tmp_path = os.path.join(TMP_DIR, "step_export.tmp") if os.path.isdir(TMP_DIR) \
        else tempfile.gettempdir() + os.sep + "step_export.tmp"
    ok = Part.export([obj], tmp_path)
    if ok is False or not os.path.exists(tmp_path) or os.path.getsize(tmp_path) < 2000:
        # fallback: прямое API
        obj.Shape.exportStep(path)
    else:
        if os.path.exists(path):
            os.remove(path)
        os.replace(tmp_path, path)
    return path


def export_all(doc, shape, basename):
    """Экспорт STL/STEP по имени basename (без расширения)."""
    out = {}
    if P.EXPORT_STL:
        out["stl"] = export_stl(shape, basename + ".stl")
    if P.EXPORT_STEP:
        out["step"] = export_step(shape, basename + ".step")
    return out


# ===========================================================================
#  Примитивы и хелперы геометрии
# ===========================================================================
def box(x, y, z, length, width, height):
    """Бокс с углом (x,y,z) и размерами. Возвращает shape."""
    s = Part.makeBox(length, width, height)
    s.translate(App.Vector(x, y, z))
    return s


def box_center(cx, cy, cz, length, width, height):
    """Бокс, отцентрованный по (cx,cy,cz)."""
    return box(cx - length / 2.0, cy - width / 2.0, cz - height / 2.0,
               length, width, height)


def cyl(axis_point, direction, radius, height):
    """Цилиндр от точки axis_point по направлению direction."""
    d = App.Vector(*direction)
    d.normalize()
    return Part.makeCylinder(radius, height, App.Vector(*axis_point), d)


def cyl_z(cx, cy, z0, radius, height):
    """Цилиндр вдоль +Z (отверстие/бобышка вертикально)."""
    return cyl((cx, cy, z0), (0, 0, 1), radius, height)


def cyl_y(cx, cz, y0, radius, height):
    """Цилиндр вдоль +Y (сквозь переднюю/заднюю панель)."""
    return cyl((cx, y0, cz), (0, 1, 0), radius, height)


def cyl_x(cy, cz, x0, radius, height):
    """Цилиндр вдоль +X (сквозь боковину)."""
    return cyl((x0, cy, cz), (1, 0, 0), radius, height)


def cone_z(cx, cy, z0, r_bottom, r_top, height):
    """Усечённый конус вдоль +Z от z0 до z0+height."""
    c = Part.makeCone(r_bottom, r_top, height)
    c.translate(App.Vector(cx, cy, z0))
    return c


def cone_x(cy, cz, x0, r_bottom, r_top, height):
    """Усечённый конус вдоль +X от x0 до x0+height."""
    c = Part.makeCone(r_bottom, r_top, height)
    c.rotate(App.Vector(0, 0, 0), App.Vector(0, 1, 0), 90)
    c.translate(App.Vector(x0, cy, cz))
    return c


def rounded_box(x, y, z, l, w, h, r, r_axis="Z"):
    """
    Бокс со скруглёнными рёбрами. Скругление по рёбрам, параллельным r_axis.
    r = 0 -> обычный бокс.
    """
    s = box(x, y, z, l, w, h)
    if r <= 0:
        return s
    sel = _edges_parallel(s, r_axis)
    if sel:
        s = s.makeFillet(r, sel)
    return s


def _edges_parallel(shape, axis):
    """Выбрать рёбра, параллельные оси axis ('X'|'Y'|'Z')."""
    idx = {"X": 0, "Y": 1, "Z": 2}[axis]
    sel = []
    for e in shape.Edges:
        v = e.tangentAt(e.FirstParameter)
        a = (abs(v.x), abs(v.y), abs(v.z))
        # вектор параллелен оси, если остальные компоненты ~0
        other = [a[i] for i in range(3) if i != idx]
        if max(other) < 1e-6 and a[idx] > 1e-6:
            sel.append(e)
    return sel


def fillet_vertical_edges(shape, radius):
    """Скруглить все вертикальные (//Z) рёбра фигуры."""
    sel = _edges_parallel(shape, "Z")
    if not sel:
        return shape
    return shape.makeFillet(radius, sel)


def cut(base, *tools):
    r = base
    for t in tools:
        r = r.cut(t)
    return r


def fuse(base, *tools):
    r = base
    for t in tools:
        r = r.fuse(t)
    return r


# ===========================================================================
#  Типовые конструктивы
# ===========================================================================
def boss(cx, cy, z0, d=None, hole_d=None, h=None):
    """
    Бобышка под самонарез M3: цилиндр с пилотным отверстием.
    Возвращает shape, которую надо fuse к корпусу.
    """
    d = P.BOSS_D if d is None else d
    hole_d = P.BOSS_HOLE_D if hole_d is None else hole_d
    h = P.BOSS_H if h is None else h
    outer = cyl_z(cx, cy, z0, d / 2.0, h)
    return cut(outer, cyl_z(cx, cy, z0, hole_d / 2.0, h + 0.1))


def vent_slots_x(x0, x1, cy_center, cz_center, span_y, span_z):
    """
    Массив щелей-жабер, пробивающих стенку вдоль оси X (боковина).
    x0..x1 — толщина стенки (с запасом).
    Раскладка — сетка VENT_ROWS x VENT_COLS внутри области span_y x span_z.
    """
    tools = []
    rows, cols = P.VENT_ROWS, P.VENT_COLS
    if rows <= 0 or cols <= 0:
        return tools
    pitch_y = P.VENT_SLOT_W + P.VENT_SLOT_GAP
    pitch_z = P.VENT_ROW_H + P.VENT_ROW_GAP
    total_w = cols * P.VENT_SLOT_W + (cols - 1) * P.VENT_SLOT_GAP
    total_h = rows * P.VENT_ROW_H + (rows - 1) * P.VENT_ROW_GAP
    if total_w > span_y or total_h > span_z:
        raise ValueError("жабры не помещаются в область: нужно %.1fx%.1f, есть %.1fx%.1f"
                         % (total_w, total_h, span_y, span_z))
    y_start = cy_center - total_w / 2.0
    z_start = cz_center - total_h / 2.0
    depth = (x1 - x0)
    for r in range(rows):
        for c in range(cols):
            y = y_start + c * pitch_y
            z = z_start + r * pitch_z
            tools.append(box(x0, y, z, depth, P.VENT_SLOT_W, P.VENT_ROW_H))
    return tools


def tongue(length, thick, height, cx, cy, cz):
    """Шип (выступ) — бокс, отцентрованный по cx/cy/cz."""
    return box_center(cx, cy, cz, length, thick, height)


def groove(length, thick, height, cx, cy, cz, clear=None):
    """Паз под шип (вырез) с зазором."""
    c = P.TONGUE_CLEAR if clear is None else clear
    return box_center(cx, cy, cz, length + 2 * c, thick + 2 * c, height + c)


# ===========================================================================
#  Информация
# ===========================================================================
def report(shape, title=""):
    bb = shape.BoundBox
    print("=" * 68)
    print("  %s" % title)
    print("  BBox : X %.2f..%.2f (%.2f)  Y %.2f..%.2f (%.2f)  Z %.2f..%.2f (%.2f)"
          % (bb.XMin, bb.XMax, bb.XLength,
             bb.YMin, bb.YMax, bb.YLength,
             bb.ZMin, bb.ZMax, bb.ZLength))
    print("  Volume: %.1f mm^3   Solids: %d  Faces: %d"
          % (shape.Volume, len(shape.Solids), len(shape.Faces)))
    print("  valid : %s" % shape.isValid())
    print("=" * 68)
    return shape


def main_guard(fn):
    """Обёртка запуска: проверка params + перехват ошибок с понятным текстом."""
    if not HAVE_FC:
        print("[ERR] FreeCAD API недоступен. Запустите через freecadcmd или GUI.")
        sys.exit(1)
    problems = P.sanity_check()
    if problems:
        print("[ERR] params.py: проблемы раскладки:")
        for p in problems:
            print("      -", p)
        sys.exit(2)
    try:
        return fn()
    except Exception as exc:                            # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("[ERR] %s: %s" % (type(exc).__name__, exc))
        sys.exit(3)
