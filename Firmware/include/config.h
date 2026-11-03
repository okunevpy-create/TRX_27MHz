#pragma once
// TRX 27 MHz — константы прошивки и сохраняемые настройки.

#include <Arduino.h>

// ===== Частотный план (docs/design_decisions_stage3.md) =====
// ПЧ = BFO = 10 МГц. RX: RF = VFO − IF; TX: RF = VFO − BFO. Отсюда VFO = RF + 10 МГц.
// Физические константы (IF_HZ, BFO_HZ) и математика VFO/BFO — в include/rf_math.h.
constexpr int32_t  BFO_OFFSET_HZ  = 0;           // отстрой BFO от центра кварцевого фильтра (bring-up, ±1.5 кГц, выбор боковой SSB)
constexpr uint32_t VFO_NOMINAL_HZ = 37000000UL;  // ~37 МГц (RF 27 МГц)
constexpr uint32_t STEP_5K_HZ     = 5000UL;
constexpr uint32_t STEP_10K_HZ    = 10000UL;

// Абсолютные границы перестройки (покрывают EU и RUS).
constexpr uint32_t RF_BAND_MIN_HZ = 26960000UL;  // 26.960 МГц (RUS ch1)
constexpr uint32_t RF_BAND_MAX_HZ = 27405000UL;  // 27.405 МГц (EU ch40)

// ===== RIT (расстройка SSB) =====
constexpr int32_t  RIT_MAX_HZ        = +1000;
constexpr int32_t  RIT_MIN_HZ        = -1000;
constexpr uint32_t RIT_STEP_FINE_HZ  = 10;
constexpr uint32_t RIT_STEP_COARSE_HZ = 100;

// ===== Пороги нажатий (мс) — docs/firmware_ui_ux.md §4 =====
constexpr uint16_t DEBOUNCE_MS = 5;
constexpr uint16_t CLICK_MS    = 300;   // короткое
constexpr uint16_t LONG_MS     = 700;   // длинное
constexpr uint16_t DOUBLE_MS   = 350;   // окно двойного

// ===== Периоды фоновых задач (мс) =====
constexpr uint16_t SI5351_UPDATE_MS = 100;  // плавность RIT (без щелчков)
constexpr uint16_t SQUELCH_MS       = 20;
constexpr uint16_t ADC_MS           = 50;
constexpr uint16_t UI_REDRAW_MS     = 50;
constexpr uint16_t MENU_TIMEOUT_MS  = 10000;

// ===== Si5351 =====
constexpr uint32_t SI5351_REF_HZ = 27600000UL; // TCXO TG2520SMN 27.6 МГц (BOM §1.3)

// ===== EEPROM (AT24C02C, 256 байт) =====
constexpr uint8_t EEPROM_I2C_ADDR = 0x50;      // A0/A1/A2 → GND

// ===== Настройки (сохраняются в EEPROM) =====
constexpr uint8_t SETTINGS_MAGIC   = 0x5A;
constexpr uint8_t SETTINGS_VERSION = 1;

enum class Mode : uint8_t { SSB = 0, AM = 1 };

// Внимание: порядок полей важен для совместимости EEPROM между прошивками.
struct Settings {
    uint8_t  magic = SETTINGS_MAGIC;
    uint8_t  version = SETTINGS_VERSION;
    uint8_t  grid = 0;         // 0=EU, 1=RUS
    uint8_t  mode = 0;         // 0=SSB, 1=AM
    uint8_t  step = 0;         // 0=5 кГц, 1=10 кГц
    uint8_t  squelch = 3;      // 0..9 (0=выкл)
    uint8_t  ritStep = 0;      // 0=10 Гц, 1=100 Гц
    uint8_t  ritAutoreset = 1; // 1=сброс RIT при смене канала
    uint8_t  brightness = 80;  // 0..100 %
    uint16_t channel = 15;     // 1..40
    int16_t  ritHz = 0;        // −1000..+1000
};
