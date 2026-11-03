#pragma once
#include <stdint.h>

// Частотная математика тракта (без Arduino) — тестируемо в native (`pio test -e native`).
// ПЧ = BFO = 10 МГц. RX: RF = VFO − IF; TX: RF = VFO − BFO. Отсюда VFO = RF + IF.
// RIT (расстройка приёма) прибавляется только в SSB и только на приём (не в TX).
// Источник: docs/design_decisions_stage3.md; ранее лежало в src/app.cpp (вынесено 2026-11-03).

constexpr uint32_t IF_HZ  = 10000000UL;  // ПЧ (10 МГц)
constexpr uint32_t BFO_HZ = 10000000UL;  // BFO (номинал, центр фильтра)

// VFO для заданной частоты RF (Гц). RIT действует только при modeSsb && !ptt.
inline uint32_t vfoHz(uint32_t rfHz, bool modeSsb, bool ptt, int32_t ritHz) {
    int64_t v = (int64_t)rfHz + IF_HZ + ((modeSsb && !ptt) ? ritHz : 0);
    if (v < 0) v = 0;
    return (uint32_t)v;
}

// BFO с отстроем от центра кварцевого фильтра (выбор боковой SSB).
inline uint32_t bfoHz(int32_t offsetHz) {
    int32_t hz = (int32_t)BFO_HZ + offsetHz;
    return (uint32_t)hz;
}
