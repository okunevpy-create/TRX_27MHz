#pragma once
// Минимальный шам Arduino.h для native-тестов чистой логики (pio test -e native).
// Даёт stdint-типы (как у настоящего Arduino.h) и заглушки digitalRead/pinMode,
// чтобы реальный src/inputs.cpp собирался и исполнялся на ПК.
#include <stdint.h>

#ifndef LOW
#define LOW           0
#define HIGH          1
#define INPUT         0
#define OUTPUT        1
#define INPUT_PULLUP  2
#endif

// Таблица состояний пинов (одна на TU). level: LOW/HIGH.
static uint8_t g_testPins[64];

inline void setPin(uint8_t pin, int level)          { g_testPins[pin & 0x3F] = (uint8_t)level; }
inline int  digitalRead(uint8_t pin)                { return g_testPins[pin & 0x3F] ? HIGH : LOW; }
inline void digitalWrite(uint8_t pin, uint8_t val)  { g_testPins[pin & 0x3F] = val; }
inline void pinMode(uint8_t pin, uint8_t mode)      { (void)pin; (void)mode; }
