#pragma once
// TRX 27 MHz — плата управления (01_control)
// Единая точка истины для маппинга GPIO.
// Источник: docs/firmware_ui_ux.md §1 + docs/bom/stage1_control.md §1.5.
// Все кнопки/энкодер — активный низкий уровень (замыкание на GND, pull-up 10 кОм на плате).

#include <Arduino.h>

// ---- Дисплей ST7789 (SPI1 + программные CS/DC/RST, подсветка PWM) ----
#define PIN_LCD_SCK    PA5    // SPI1 SCK
#define PIN_LCD_MOSI   PA7    // SPI1 MOSI
#define PIN_LCD_CS     PA4    // SPI_CS  (GPIO)
#define PIN_LCD_DC     PA6    // SPI_DC  (GPIO)
#define PIN_LCD_RST    PA3    // LCD_RST (GPIO)
#define PIN_LCD_BL     PB0    // LCD_BLK (PWM, active-low ключ Q1)

// ---- Энкодер HW-040 (CLK/DT/SW) ----
#define PIN_ENC_CLK    PB12
#define PIN_ENC_DT     PB13
#define PIN_ENC_SW     PB14

// ---- Джойстик 5-поз. + кнопка RIT (J_BTN_1) ----
#define PIN_BTN_UP     PC13
#define PIN_BTN_DOWN   PC14
#define PIN_BTN_LEFT   PC15
#define PIN_BTN_RIGHT  PB1
#define PIN_BTN_PUSH   PB2
#define PIN_BTN_RIT    PB15

// ---- PTT ----
#define PIN_PTT_IN     PB5    // вход с гарнитуры (active-low: 0 = передача)
#define PIN_PTT_OUT    PA8    // выход на PA/RX-TX (0/3.3 В, 1 = TX)

// ---- Режим / squelch / ограничитель ----
#define PIN_MODE          PB9   // 0=SSB, 1=AM
#define PIN_MUTE          PB8   // 1=заглушить УНЧ
#define PIN_PWR_LIMIT_EN  PB10  // 1=программно включить ограничитель (резерв)
#define PIN_PWR_LIMIT_SW  PA11  // вход: 1=LIMIT, 0=FULL

// ---- ADC ----
#define PIN_ADC_I_SENSE   PA0   // ток УМ
#define PIN_ADC_SWR       PA1   // КСВ
#define PIN_ADC_RX_AUDIO  PA2   // RX_audio (squelch)

// ---- I2C (Si5351 + EEPROM AT24C02C) ----
#define PIN_I2C_SCL     PB6
#define PIN_I2C_SDA     PB7
