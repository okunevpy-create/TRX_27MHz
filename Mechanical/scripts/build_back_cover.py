# -*- coding: utf-8 -*-
"""
build_back_cover.py — ЗАДНЯЯ КРЫШКА корпуса — этап 4.

Плоская панель 186 x 56 (углы R2.5), закрывающая задний проём корпуса.
Стыкуется к скорлупам: 8 язычков (2 сверху + 2 снизу + 2 слева + 2 справа)
входят в задние пазы скорлуп (см. build_shells.rear_join_feature), винт M3 Ø3.4
проходит сквозь язычок в бобышку скорлупы; на наружной грани — конусная зенковка
под потайную головку (винт снаружи внутрь).

СК (совпадает с остальными деталями):
    x : -3..183 (наружный габарит 186)
    y : 0 — фронт, +Y внутрь; задний торец скорлуп на CASE_D=160
    z : -3..53 (наружный габарит 56)

Запуск:  freecadcmd Mechanical/scripts/build_back_cover.py
"""

import os

import fc_common as C
from fc_common import App, Part, P
from build_front_panel import panel_dims, screw_positions, rounded_rect, extrude_xz


def build():
    x0, z0, length, height = panel_dims()
    y_back = P.CASE_D
    t = P.T_BACK

    # Плоская панель (углы R2.5), выступает назад от заднего торца скорлуп.
    panel = extrude_xz(rounded_rect(x0, z0, length, height, P.CORNER_R),
                       y_back, t)

    # Язычок = GROOVE_W; паз в скорлупе = GROOVE_W + GROOVE_CLEAR (зазор).
    gw = P.GROOVE_W
    gh = P.GROOVE_H
    gl = P.GROOVE_L
    y_start = y_back - gl + P.GROOVE_FLOOR_GAP
    y_center = y_back - gl / 2.0

    screw_r = P.JOIN_SCREW_D / 2.0
    csk_d = P.JOIN_SCREW_CSK_DEPTH
    csk_r_big = P.SCREW_HEAD_D / 2.0               # у поверхности (снаружи)
    csk_r_small = P.JOIN_SCREW_D / 2.0             # у дна зенковки

    adds, cuts = [], []
    for _name, ca, _y, axis in screw_positions(y_c=y_center):
        if axis == "Z":
            z_face = (z0 + height - gh) if _name.startswith("top") else z0
            adds.append(C.box(ca - gw / 2.0, y_start, z_face, gw, gl, gh))
            cuts.append(C.cyl_z(ca, y_center, z_face, screw_r, gh))
            # конусная зенковка: большим диаметром к наружной грани
            if _name.startswith("top"):
                cuts.append(C.cone_z(ca, y_center, z_face + gh - csk_d,
                                     csk_r_small, csk_r_big, csk_d))
            else:
                cuts.append(C.cone_z(ca, y_center, z0, csk_r_big, csk_r_small, csk_d))
        else:
            x_from = x0 if _name.startswith("left") else (x0 + length - gh)
            adds.append(C.box(x_from, y_start, ca - gw / 2.0, gh, gl, gw))
            cuts.append(C.cyl_x(y_center, ca, x_from, screw_r, gh))
            # конусная зенковка: большим диаметром к наружной грани
            if _name.startswith("left"):
                cuts.append(C.cone_x(y_center, ca, x0, csk_r_big, csk_r_small, csk_d))
            else:
                cuts.append(C.cone_x(y_center, ca, x_from + gh - csk_d,
                                     csk_r_small, csk_r_big, csk_d))

    body = C.fuse(panel, *adds)
    body = C.cut(body, *cuts)
    return body.removeSplitter()


def _bop_status(shape):
    """BOP-проверка: CLEAN, если check(True) вернул None/True."""
    try:
        res = shape.check(True)
    except Exception as exc:                            # noqa: BLE001
        return "ERROR: %r" % (exc,)
    return "CLEAN" if (res is None or res is True) else "FAIL: %r" % (res,)


def run():
    problems = P.sanity_check()
    if problems:
        print("[ERR] params.py:")
        for x in problems:
            print("      -", x)
        return 2

    doc = C.new_doc("back_cover")
    body = build()
    C.report(body, "ЗАДНЯЯ КРЫШКА")
    print("       BOP check : %s" % _bop_status(body))

    C.add_shape(doc, body, "BackCover", "Задняя крышка")
    print("[OK] FCStd :", C.save_fcstd(doc, "back_cover.FCStd"))
    for k, v in C.export_all(doc, body, "back_cover").items():
        print("[OK] %-4s : %s" % (k.upper(), v))
    print("[DONE] back_cover")
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
