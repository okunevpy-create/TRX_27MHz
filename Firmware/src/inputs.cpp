#include "inputs.h"

// ---- Button ----

void Button::update(uint32_t nowMs) {
    bool raw = ((digitalRead(_pin) == LOW) == _activeLow); // true = нажата
    if (raw != _raw) {
        // антидребезг: фиксируем переключение после DEBOUNCE_MS стабильности
        if (nowMs - _changeMs >= DEBOUNCE_MS) {
            _raw = raw;
            _changeMs = nowMs;
            if (_raw) {
                _tDown = nowMs;
                _longFired = false;
            } else {
                _tUp = nowMs;
                if (!_longFired) {
                    if (_clickPending) {
                        _pending = BtnEvent::DOUBLE; // второй отклик в окне
                        _clickPending = false;
                    } else {
                        _clickPending = true; // CLICK отложен до истечения окна
                    }
                }
            }
        }
    } else {
        _changeMs = nowMs;
    }

    // Длинное нажатие — пока кнопка удерживается.
    if (_raw && !_longFired && (nowMs - _tDown >= LONG_MS)) {
        _longFired = true;
        _clickPending = false;
        _pending = BtnEvent::LONG;
    }

    // Отложенный CLICK: если второго нажатия в окне не было.
    if (_clickPending && !_raw && (nowMs - _tUp >= DOUBLE_MS)) {
        _clickPending = false;
        _pending = BtnEvent::CLICK;
    }
}

BtnEvent Button::event() {
    BtnEvent e = _pending;
    _pending = BtnEvent::NONE;
    return e;
}

// ---- Encoder ----

void Encoder::begin() {
    pinMode(_clk, INPUT_PULLUP);
    pinMode(_dt, INPUT_PULLUP);
    _sw.begin();
    _lastA = (digitalRead(_clk) == LOW);
}

void Encoder::update(uint32_t nowMs) {
    bool a = (digitalRead(_clk) == LOW);   // нормализуем: true = замкнут
    bool b = (digitalRead(_dt) == LOW);
    if (a != _lastA && a) {                // фронт CLK (замыкание контакта)
        int8_t d = (b == a) ? +1 : -1;     // направление (уточнить на bring-up)
        _acc += _invert ? -d : d;
    }
    _lastA = a;
    _sw.update(nowMs);
}

int16_t Encoder::readDelta() {
    int16_t d = _acc;
    _acc = 0;
    return d;
}
