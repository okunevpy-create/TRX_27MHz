#pragma once
#include <Arduino.h>
#include "config.h"

// Событие кнопки (по фронтам). Для уровня (PTT) использовать pressed().
enum class BtnEvent : uint8_t { NONE = 0, CLICK, DOUBLE, LONG };

class Button {
public:
    Button() = default;
    Button(uint8_t pin, bool activeLow = true) : _pin(pin), _activeLow(activeLow) {}

    void assign(uint8_t pin, bool activeLow = true) {
        _pin = pin;
        _activeLow = activeLow;
    }

    void begin() { pinMode(_pin, INPUT_PULLUP); }

    // Вызывать каждые ~1 мс.
    void update(uint32_t nowMs);

    // Текущее (антидребезг) состояние: true = нажата.
    bool pressed() const { return _raw; }

    // Забрать одно отложенное фронтовое событие (CLICK/DOUBLE/LONG).
    BtnEvent event();

    uint32_t held(uint32_t nowMs) const { return _raw ? (nowMs - _tDown) : 0; }

private:
    uint8_t  _pin = 0;
    bool     _activeLow = true;
    bool     _raw = false;          // дебаунс-состояние
    bool     _longFired = false;
    bool     _clickPending = false; // ждём: не двойное ли нажатие
    uint32_t _tDown = 0;
    uint32_t _tUp = 0;
    uint32_t _changeMs = 0;
    BtnEvent _pending = BtnEvent::NONE;
};

class Encoder {
public:
    Encoder() = default;
    Encoder(uint8_t clk, uint8_t dt, uint8_t sw) : _clk(clk), _dt(dt), _sw(sw, true) {}

    void assign(uint8_t clk, uint8_t dt, uint8_t sw) {
        _clk = clk;
        _dt = dt;
        _sw.assign(sw, true);
    }

    void begin();
    void update(uint32_t nowMs);   // опрос CLK/DT + кнопки SW

    int16_t readDelta();           // накопленный поворот с последнего чтения

    Button& button() { return _sw; }
    void setInvert(bool inv) { _invert = inv; }

private:
    uint8_t _clk = 0, _dt = 0;
    bool    _lastA = false;
    int16_t _acc = 0;
    bool    _invert = false;
    Button  _sw;
};
