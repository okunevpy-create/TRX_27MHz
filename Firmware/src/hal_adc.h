#pragma once
#include <Arduino.h>

class Adc {
public:
    void begin();               // 12-бит
    uint16_t readI();           // I_sense (усреднённый)
    uint16_t readSwr();         // SWR_sense
    uint16_t readRxAudio();     // RX_audio (RMS-отклонение от среднего, для squelch)
private:
    uint16_t _avg(uint8_t pin, uint8_t n);
    uint16_t _rxMean = 0;
};
