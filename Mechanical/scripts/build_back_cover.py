# -*- coding: utf-8 -*-
"""
build_back_cover.py — ЗАДНЯЯ КРЫШКА корпуса — этап 4.

Плоская панель 186 x 56 (углы R2.5), закрывающая задний проём корпуса.
Стыкуется к скорлупам: 4 язычка (2 сверху + 2 снизу) входят в задние пазы
скорлуп (см. build_shells.rear_join_feature), винт M3 Ø3.4 проходит сквозь
язычок в бобышку скорлупы.

СК (совпадает с остальными деталями):
    x : -3..183 (наружный габарит 186)
    y : 0 — фронт, +Y внутрь; задний торец скорлуп на CASE_D=160
    z : -3..53 (наружный габарит 56)

Запуск:  freecadcmd Mechanical/scripts/build_back_cover.py
"""

import os

import fc_common as C
from fc_common import App, Part, P
from build_front_panel import panel_dims, rounded_rect, extrude_xz


def _rear_screw_positions():
    """[(side, ca, y_c, z_face)] — оси винтов задней крышки.

    Зеркалит раскладку задних пазов скорлуп из build_shells.rear_join_feature.
    """
    x0, z0, length, height = panel_dims()
    y_c = P.CASE_D - P.GROOVE_L / 2.0
    gh = P.GROOVE_H
    pos = []
    for i in range(P.REAR_JOIN_SCREWS_TOP):
        f = (i + 1.0) / (P.REAR_JOIN_SCREWS_TOP + 1.0)
        pos.append(("top", x0 + f * length, y_c, z0 + height - gh))
    for i in range(P.REAR_JOIN_SCREWS_BOTTOM):
        f = (i + 1.0) / (P.REAR_JOIN_SCREWS_BOTTOM + 1.0)
        pos.append(("bottom", x0 + f * length, y_c, z0))
    return pos


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

    adds, cuts = [], []
    for _side, ca, y_c, z_face in _rear_screw_positions():
        adds.append(C.box(ca - gw / 2.0, y_start, z_face, gw, gl, gh))
        cuts.append(C.cyl_z(ca, y_c, z_face, P.JOIN_SCREW_D / 2.0, gh))

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
