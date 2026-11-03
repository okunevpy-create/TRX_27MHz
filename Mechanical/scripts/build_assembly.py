# -*- coding: utf-8 -*-
"""
build_assembly.py — СБОРОЧНЫЙ МАКЕТ корпуса — этап 4.

Соединяет все детали в одном документе:
    передняя панель + верхняя скорлупа + нижняя скорлупа + задняя крышка.
На места установки органов управления добавляет СХЕМАТИЧНЫЕ модели
(простые боксы/цилиндры), чтобы визуализировать посадку.

СК — глобальная (совпадает с деталями): детали уже стоят на своих местах,
сборка лишь кладёт их в один документ и добавляет компоненты.

Запуск:  freecadcmd Mechanical/scripts/build_assembly.py
"""

import os

import fc_common as C
from fc_common import App, Part, P
import build_front_panel as FP
import build_shells as SH
import build_back_cover as BC


def _box(cx, cy, cz, l_x, w_y, h_z):
    """Бокс, отцентрованный по (cx, cy, cz); размеры по X/Y/Z."""
    return C.box(cx - l_x / 2.0, cy - w_y / 2.0, cz - h_z / 2.0, l_x, w_y, h_z)


def schematic_controls():
    """[(name, shape)] — схематичные модели органов управления."""
    y_in = P.T_PANEL
    out = []

    # Экран ST7789 2.0" (плата + стекло) — за панелью на стойках
    sy = y_in + P.SCR_STANDOFF_H + P.SCR_SCHEMA_T / 2.0
    out.append(("Screen", _box(P.SCR_CENTER_X, sy, P.SCR_CENTER_Z,
                               P.SCR_PCB_W, P.SCR_SCHEMA_T, P.SCR_PCB_H)))

    # Энкодер HW-040: плата модуля 26×18 + втулка сквозь панель.
    # Вал смещён ОТ края с отверстиями на ENC_SHAFT_DZ (по Z, узкая сторона).
    ey = y_in + P.ENC_STANDOFF_H + P.ENC_SCHEMA_T / 2.0
    bz = P.ENC_CENTER_Z + P.ENC_SHAFT_DZ
    enc = _box(P.ENC_CENTER_X, ey, bz,
               P.ENC_BOARD_W, P.ENC_SCHEMA_T, P.ENC_BOARD_H)
    enc = enc.fuse(C.cyl_y(P.ENC_CENTER_X, P.ENC_CENTER_Z, -2.0,
                           P.ENC_BUSHING_D / 2.0, P.T_PANEL + 4.0))
    out.append(("Encoder", enc))

    # Джойстик: плата + штырёк (наружу)
    jy = y_in + P.JOY_STANDOFF_H + P.JOY_SCHEMA_T / 2.0
    joy = _box(P.JOY_CENTER_X, jy, P.JOY_CENTER_Z,
               P.JOY_BOARD_W, P.JOY_SCHEMA_T, P.JOY_BOARD_H)
    joy = joy.fuse(C.cyl_y(P.JOY_CENTER_X, P.JOY_CENTER_Z, -P.JOY_SHAFT_H,
                           P.JOY_SHAFT_D / 2.0, P.JOY_SHAFT_H + P.T_PANEL))
    out.append(("Joystick", joy))

    # Тумблер питания KN3: корпус + втулка + рычажок (наружу)
    ty = y_in + P.PWR_SW_SCHEMA_D / 2.0
    tog = _box(P.PWR_SW_CENTER_X, ty, P.PWR_SW_CENTER_Z,
               P.PWR_SW_SCHEMA_W, P.PWR_SW_SCHEMA_D, P.PWR_SW_SCHEMA_H)
    tog = tog.fuse(C.cyl_y(P.PWR_SW_CENTER_X, P.PWR_SW_CENTER_Z, -2.0,
                           P.PWR_SW_HOLE_D / 2.0, P.T_PANEL + 4.0))
    tog = tog.fuse(_box(P.PWR_SW_CENTER_X, -P.PWR_SW_SCHEMA_LEVER / 2.0,
                        P.PWR_SW_CENTER_Z, 4.0, P.PWR_SW_SCHEMA_LEVER, 4.0))
    out.append(("PowerSwitch", tog))

    # Тумблер LIMIT/FULL (ASW-14-102): корпус + втулка + рычажок (наружу)
    ly = y_in + P.LIM_SW_SCHEMA_D / 2.0
    limt = _box(P.LIM_SW_CENTER_X, ly, P.LIM_SW_CENTER_Z,
                P.LIM_SW_SCHEMA_W, P.LIM_SW_SCHEMA_D, P.LIM_SW_SCHEMA_H)
    limt = limt.fuse(C.cyl_y(P.LIM_SW_CENTER_X, P.LIM_SW_CENTER_Z, -2.0,
                             P.LIM_SW_HOLE_D / 2.0, P.T_PANEL + 4.0))
    limt = limt.fuse(_box(P.LIM_SW_CENTER_X, -P.LIM_SW_SCHEMA_LEVER / 2.0,
                          P.LIM_SW_CENTER_Z, 4.0, P.LIM_SW_SCHEMA_LEVER, 4.0))
    out.append(("LimitSwitch", limt))

    # Светодиоды (горизонтальная линия из 3 шт наверху)
    for nm, cx, cz in P.led_positions():
        led = C.cyl_y(cx, cz, -2.0, P.LED_HOLE_D / 2.0, P.T_PANEL + 4.0)
        led = led.fuse(C.cyl_y(cx, cz, y_in, P.LED_BEZEL_D / 2.0, P.LED_SCHEMA_D))
        out.append(("LED_" + nm, led))

    # Гарнитура 3.5 / 2.5 мм
    for nm, cz, hole_d, seal_d in (
            ("Headset35", P.HS_35_CENTER_Z, P.HS_35_HOLE_D, P.HS_SEAL_D),
            ("Headset25", P.HS_25_CENTER_Z, P.HS_25_HOLE_D, P.HS_SEAL_D_25)):
        hs = C.cyl_y(P.HS_CENTER_X, cz, -2.0, hole_d / 2.0, P.T_PANEL + 4.0)
        hs = hs.fuse(C.cyl_y(P.HS_CENTER_X, cz, y_in, seal_d / 2.0, P.HS_SCHEMA_D))
        out.append((nm, hs))

    # Кнопка RIT: втулка + корпус за панелью
    rit = C.cyl_y(P.RIT_CENTER_X, P.RIT_CENTER_Z, -2.0,
                  P.RIT_HOLE_D / 2.0, P.T_PANEL + 4.0)
    rit = rit.fuse(C.cyl_y(P.RIT_CENTER_X, P.RIT_CENTER_Z, y_in,
                           P.RIT_BEZEL_D / 2.0, P.RIT_SCHEMA_D))
    out.append(("RitButton", rit))

    return out


def schematic_back_controls():
    """[(name, shape)] — схематичные модели разъёмов задней крышки."""
    y_in = P.CASE_D              # внутренняя грань задней крышки (y=160)
    out = []

    def body(cx, cz, d, depth):
        # цилиндр тела разъёма внутрь корпуса (−Y) от внутренней грани
        return C.cyl((cx, y_in, cz), (0, -1, 0), d / 2.0, depth)

    def bushing(cx, cz, hole_d):
        # втулка сквозь панель (с запасом в обе стороны)
        return C.cyl_y(cx, cz, y_in - 2.0, hole_d / 2.0, P.T_BACK + 6.0)

    # Антенна BNC
    ant = bushing(P.ANT_CENTER_X, P.ANT_CENTER_Z, P.ANT_HOLE_D)
    ant = ant.fuse(body(P.ANT_CENTER_X, P.ANT_CENTER_Z,
                        P.ANT_SCHEMA_BODY, P.ANT_SCHEMA_D))
    out.append(("Antenna", ant))

    # Разъём питания DC
    dc = bushing(P.PWR_CONN_CENTER_X, P.PWR_CONN_CENTER_Z, P.PWR_CONN_HOLE_D)
    dc = dc.fuse(body(P.PWR_CONN_CENTER_X, P.PWR_CONN_CENTER_Z,
                      P.PWR_CONN_SCHEMA_BODY, P.PWR_CONN_SCHEMA_D))
    out.append(("DCJack", dc))

    # Держатель предохранителя (корпус + колпачок наружу)
    fu = bushing(P.FUSE_CENTER_X, P.FUSE_CENTER_Z, P.FUSE_HOLE_D)
    fu = fu.fuse(body(P.FUSE_CENTER_X, P.FUSE_CENTER_Z,
                      P.FUSE_SCHEMA_BODY, P.FUSE_SCHEMA_D))
    fu = fu.fuse(C.cyl_y(P.FUSE_CENTER_X, P.FUSE_CENTER_Z, y_in + P.T_BACK,
                         P.FUSE_SCHEMA_CAP_D / 2.0, 6.0))
    out.append(("FuseHolder", fu))

    return out


def run():
    problems = P.sanity_check()
    if problems:
        print("[ERR] params.py:")
        for x in problems:
            print("      -", x)
        return 2

    doc = C.new_doc("assembly")

    print("[1/5] Передняя панель")
    front = FP.build()
    print("[2/5] Верхняя скорлупа")
    top = SH.build("top")
    print("[3/5] Нижняя скорлупа")
    bottom = SH.build("bottom")
    print("[4/5] Задняя крышка")
    back = BC.build()

    C.add_shape(doc, front, "FrontPanel", "Передняя панель")
    C.add_shape(doc, top, "ShellTop", "Верхняя скорлупа")
    C.add_shape(doc, bottom, "ShellBottom", "Нижняя скорлупа")
    C.add_shape(doc, back, "BackCover", "Задняя крышка")

    print("[5/5] Органы управления (схематично)")
    controls = schematic_controls()
    for name, shape in controls:
        C.add_shape(doc, shape, "Ctrl_" + name, "Схема: " + name)

    print("[6/6] Разъёмы задней крышки (схематично)")
    back_controls = schematic_back_controls()
    for name, shape in back_controls:
        C.add_shape(doc, shape, "Ctrl_" + name, "Схема: " + name)

    print("[OK] FCStd :", C.save_fcstd(doc, "assembly.FCStd"))

    # Сводный STL/STEP сборки (для быстрого предпросмотра).
    compound = Part.makeCompound([front, top, bottom, back] +
                                 [s for _, s in controls] +
                                 [s for _, s in back_controls])
    print("[OK] STL  :", C.export_stl(compound, "assembly.stl"))
    try:
        print("[OK] STEP :", C.export_step(compound, "assembly.step"))
    except Exception as exc:                            # noqa: BLE001
        print("[WARN] STEP сборки не экспортирован: %r" % (exc,))

    print("[DONE] assembly")
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
