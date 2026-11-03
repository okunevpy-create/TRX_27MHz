#include "hal_si5351.h"
#include "config.h"
#include <Adafruit_SI5351.h>
#include <Wire.h>

static Adafruit_SI5351 si5351 = Adafruit_SI5351(); // I2C 0x60

// Adafruit Si5351 v1.6.0 в высокоуровневом setFrequency() жёстко считает опору
// 25 МГц (и не даёт сеттера), поэтому делители считаем сами через низкоуровневые
// setupPLL()/setupMultisynth()/setupRdiv() с реальной опорой 27.6 МГц.
// Выход: fout = fxtal * (mult + num/denom) / (D * R).
static constexpr uint32_t VCO_MIN = 600000000UL;
static constexpr uint32_t VCO_MAX = 900000000UL;
static constexpr uint32_t MS_MIN  = 600000UL;   // держит D <= 1800
static constexpr uint32_t DENOM   = 0xFFFFFUL;  // 1048575 (20 бит)

// Установить частоту (Гц) на выход Si5351 (CLK0..CLK2) через PLL A или B.
// Повторяет алгоритм библиотечного setFrequency(), но с fxtal = 27.6 МГц.
static err_t setFreq(uint8_t output, si5351PLL_t pll, uint32_t freq) {
    // R-делитель: для 10–37 МГц не нужен (R=1), но сохраняем общий случай.
    uint32_t f_ms = freq;
    uint8_t rdiv = 0;
    while (f_ms < MS_MIN && rdiv < 7) {
        f_ms <<= 1;
        rdiv++;
    }

    // Наибольший чётный multisynth-делитель, держащий VCO в 600–900 МГц.
    uint32_t D = VCO_MAX / f_ms;
    if (D > 1800) D = 1800;
    D &= ~1UL;      // чётный → меньше джиттера
    if (D < 6) D = 6;

    uint32_t fvco = f_ms * D;
    if (fvco < VCO_MIN || fvco > VCO_MAX) return ERROR_INVALIDPARAMETER;

    uint32_t mult = fvco / SI5351_REF_HZ;
    uint32_t rem  = fvco % SI5351_REF_HZ;
    uint32_t num  = (uint32_t)(((uint64_t)rem * DENOM) / SI5351_REF_HZ);
    if (mult < 15 || mult > 90) return ERROR_INVALIDPARAMETER;

    err_t e = si5351.setupPLL(pll, (uint8_t)mult, num, DENOM);
    if (e != ERROR_NONE) return e;
    e = si5351.setupMultisynth(output, pll, D, 0, 1);
    if (e != ERROR_NONE) return e;
    return si5351.setupRdiv(output, (si5351RDiv_t)rdiv);
}

bool Si5351Synth::begin() {
    Wire.begin(); // PB6/PB7 (I2C1), общая с EEPROM
    _ok = (si5351.begin() == ERROR_NONE);
    if (_ok) {
        si5351.enableOutputs(true);
    }
    return _ok;
}

void Si5351Synth::setVfo(uint32_t hz) {
    if (_ok) setFreq(0, SI5351_PLL_A, hz); // CLK0 = VFO
}

void Si5351Synth::setBfo(uint32_t hz) {
    if (_ok) setFreq(1, SI5351_PLL_B, hz); // CLK1 = BFO
}

void Si5351Synth::enableOutputs(bool en) {
    if (_ok) si5351.enableOutputs(en);
}
