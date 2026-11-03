#include "hal_adc.h"
#include "pins.h"
#include <math.h>

void Adc::begin() {
    analogReadResolution(12); // 0..4095
}

uint16_t Adc::_avg(uint8_t pin, uint8_t n) {
    uint32_t s = 0;
    for (uint8_t i = 0; i < n; i++) s += analogRead(pin);
    return (uint16_t)(s / n);
}

uint16_t Adc::readI()   { return _avg(PIN_ADC_I_SENSE, 8); }
uint16_t Adc::readSwr() { return _avg(PIN_ADC_SWR, 8); }

uint16_t Adc::readRxAudio() {
    // RMS-амплитуда вокруг скользящего среднего (для squelch).
    const uint8_t N = 16;
    uint16_t samples[N];
    uint32_t sum = 0;
    for (uint8_t i = 0; i < N; i++) {
        samples[i] = analogRead(PIN_ADC_RX_AUDIO);
        sum += samples[i];
    }
    uint16_t mean = (uint16_t)(sum / N);
    _rxMean = (_rxMean == 0) ? mean : (uint16_t)((_rxMean * 3 + mean) / 4);

    uint32_t acc = 0;
    for (uint8_t i = 0; i < N; i++) {
        int32_t d = (int32_t)samples[i] - (int32_t)_rxMean;
        acc += (uint32_t)(d * d);
    }
    return (uint16_t)sqrtf((float)acc / N);
}
