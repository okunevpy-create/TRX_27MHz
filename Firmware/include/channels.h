#pragma once
#include <stdint.h>

// Канальный план CEPT (EU) 40 каналов, 26.965–27.405 МГц, шаг 10 кГц с пропусками
// на «пятёрках». RUS = EU − 5 кГц.
// Чистая логика без Arduino — тестируемо в native (`pio test -e native`).
// Источник: docs/channels.md; ранее лежала статикой в src/app.cpp (вынесено 2026-11-03).

constexpr uint8_t CHANNEL_COUNT = 40;

static const uint32_t EU_CHANNELS[CHANNEL_COUNT] = {
    26965000UL, 26975000UL, 26985000UL, 27005000UL, 27015000UL, 27025000UL, 27035000UL,
    27055000UL, 27065000UL, 27075000UL, 27085000UL, 27105000UL, 27115000UL, 27125000UL,
    27135000UL, 27155000UL, 27165000UL, 27175000UL, 27185000UL, 27205000UL, 27215000UL,
    27225000UL, 27235000UL, 27245000UL, 27255000UL, 27265000UL, 27275000UL, 27285000UL,
    27295000UL, 27305000UL, 27315000UL, 27325000UL, 27335000UL, 27345000UL, 27355000UL,
    27365000UL, 27375000UL, 27385000UL, 27395000UL, 27405000UL
};

// Частота канала (1..40) в Гц; eu=true → EU, false → RUS (−5 кГц). Границы клампятся.
inline uint32_t channelFreq(uint8_t ch, bool eu) {
    if (ch < 1) ch = 1;
    if (ch > CHANNEL_COUNT) ch = CHANNEL_COUNT;
    uint32_t f = EU_CHANNELS[ch - 1];
    return eu ? f : f - 5000UL;
}

// Ближайший канал (1..40) к заданной частоте в Гц.
inline uint8_t freqToChannel(uint32_t hz, bool eu) {
    uint8_t best = 1;
    uint32_t bestd = 0xFFFFFFFFUL;
    for (uint8_t i = 1; i <= CHANNEL_COUNT; i++) {
        uint32_t f = channelFreq(i, eu);
        uint32_t d = (hz >= f) ? (hz - f) : (f - hz);
        if (d < bestd) { bestd = d; best = i; }
    }
    return best;
}
