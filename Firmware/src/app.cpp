#include "app.h"
#include "channels.h"
#include "rf_math.h"

static constexpr uint8_t MENU_COUNT = 8;

// ===== Инициализация =====

void App::begin() {
    // I/O
    pinMode(PIN_PTT_OUT, OUTPUT);       digitalWrite(PIN_PTT_OUT, LOW);
    pinMode(PIN_MODE, OUTPUT);          digitalWrite(PIN_MODE, LOW);
    pinMode(PIN_MUTE, OUTPUT);          digitalWrite(PIN_MUTE, LOW);
    pinMode(PIN_PWR_LIMIT_EN, OUTPUT);
    pinMode(PIN_PWR_LIMIT_SW, INPUT_PULLUP);

    // модули
    _adc.begin();
    _display.begin();
    _eeprom.begin();
    _synth.begin();

    // входы
    _enc.assign(PIN_ENC_CLK, PIN_ENC_DT, PIN_ENC_SW);
    _enc.begin();
    _btnUp.assign(PIN_BTN_UP);      _btnUp.begin();
    _btnDown.assign(PIN_BTN_DOWN);  _btnDown.begin();
    _btnLeft.assign(PIN_BTN_LEFT);  _btnLeft.begin();
    _btnRight.assign(PIN_BTN_RIGHT);_btnRight.begin();
    _btnPush.assign(PIN_BTN_PUSH);  _btnPush.begin();
    _btnRit.assign(PIN_BTN_RIT);    _btnRit.begin();
    _btnPtt.assign(PIN_PTT_IN);     _btnPtt.begin();

    // настройки (EEPROM)
    if (!_eeprom.load(_s)) {
        _s = Settings{};
        _eeprom.save(_s);
    }
    _channel = _s.channel;
    _rfHz = channelFreq((uint8_t)_channel, _s.grid == 0);
    _ritHz = _s.ritHz;

    _applyMode();
    _applyPowerLimit();
    _display.setBacklight(_s.brightness);
    _synth.setBfo(bfoHz(BFO_OFFSET_HZ));
    _applyFrequency();

    _state = AppState::BOOT;
    _bootMs = millis();
    _dirty = true;
}

// ===== Главный цикл =====

void App::run() {
    uint32_t now = millis();

    // 1. Опрос входов
    _enc.update(now);
    _btnUp.update(now);
    _btnDown.update(now);
    _btnLeft.update(now);
    _btnRight.update(now);
    _btnPush.update(now);
    _btnRit.update(now);
    _btnPtt.update(now);

    // 2. PTT — наивысший приоритет
    bool pttIn = _btnPtt.pressed();
    if (pttIn != _ptt) {
        _ptt = pttIn;
        if (_ptt) { _enterTx(); _state = AppState::TX; }
        else      { _exitTx(); if (_state == AppState::TX) _state = AppState::VFO; }
        _freqDirty = true;  // пересчитать VFO: RIT действует только в RX
        _dirty = true;
    }

    // 3. Конечный автомат
    switch (_state) {
        case AppState::BOOT:
            if (now - _bootMs >= 1000) { _state = AppState::VFO; _dirty = true; }
            break;
        case AppState::VFO:  _processVfoInput(); break;
        case AppState::MENU: _processMenuInput(); break;
        case AppState::RIT:  _processRitInput(); break;
        case AppState::TX:   break; // выход только по PTT
    }

    // 4. Фоновые задачи
    if (now - _lastAdc >= ADC_MS) {
        _lastAdc = now;
        _updateMeasurements();
    }
    if (now - _lastSquelch >= SQUELCH_MS) {
        _lastSquelch = now;
        _processSquelch();
    }
    if (_freqDirty && (now - _lastSi >= SI5351_UPDATE_MS)) {
        _lastSi = now;
        _applyFrequency();
        _freqDirty = false;
    }

    // 5. Отрисовка (по изменению, с троттлингом)
    if (_dirty && (now - _lastRedraw >= UI_REDRAW_MS)) {
        _lastRedraw = now;
        _ui.render(*this);
        _dirty = false;
    }
}

// ===== Частота / синтез =====

uint32_t App::_vfoHz() const {
    return vfoHz(_rfHz, _s.mode == 0, _ptt, _ritHz);
}

void App::_applyFrequency() {
    _synth.setVfo(_vfoHz());
    _synth.setBfo(bfoHz(BFO_OFFSET_HZ));
}

void App::_applyMode() {
    digitalWrite(PIN_MODE, (_s.mode == 1) ? HIGH : LOW); // 1=AM
}

void App::_applyPowerLimit() {
    _limitSw = (digitalRead(PIN_PWR_LIMIT_SW) == HIGH); // 1=LIMIT, 0=FULL
    // Вариант C: единственный ключ — Q3 (прошивка). Лимит активен только в AM при тумблере LIMIT.
    digitalWrite(PIN_PWR_LIMIT_EN, (_s.mode == 1 && _limitSw) ? HIGH : LOW);
}

void App::_setChannel(uint16_t ch) {
    _channel = constrain((int)ch, 1, CHANNEL_COUNT);
    _rfHz = channelFreq((uint8_t)_channel, _s.grid == 0);
    if (_s.ritAutoreset) _ritHz = 0;
    _s.channel = _channel;
    _freqDirty = true;
    _dirty = true;
}

void App::_stepChannel(int16_t dir) {
    int16_t ch = (int16_t)_channel + dir;
    _setChannel((uint16_t)constrain(ch, 1, CHANNEL_COUNT));
}

void App::_stepFrequency(int32_t hz) {
    int64_t f = (int64_t)_rfHz + hz;
    if (f < RF_BAND_MIN_HZ) f = RF_BAND_MIN_HZ;
    if (f > RF_BAND_MAX_HZ) f = RF_BAND_MAX_HZ;
    _rfHz = (uint32_t)f;
    _channel = freqToChannel(_rfHz, _s.grid == 0);
    _freqDirty = true;
    _dirty = true;
}

void App::_setRit(int32_t hz) {
    _ritHz = constrain((int)hz, (int)RIT_MIN_HZ, (int)RIT_MAX_HZ);
    _s.ritHz = (int16_t)_ritHz;
    _freqDirty = true;
    _dirty = true;
}

void App::_enterTx() {
    digitalWrite(PIN_PTT_OUT, HIGH);
    _updateMeasurements();
}

void App::_exitTx() {
    digitalWrite(PIN_PTT_OUT, LOW);
}

// ===== Фоновые задачи =====

void App::_updateMeasurements() {
    _applyPowerLimit();
    uint16_t i = _adc.readI();
    uint16_t swr = _adc.readSwr();
    // bring-up: калибровочные коэффициенты TBD
    _powerW = (float)i * (10.0f / 4095.0f);
    _swr = 1.0f + (float)swr * (2.0f / 4095.0f);
}

void App::_processSquelch() {
    if (_ptt) { digitalWrite(PIN_MUTE, HIGH); return; }        // в TX глушим динамик
    if (_s.squelch == 0) { digitalWrite(PIN_MUTE, LOW); return; } // выкл → открыт
    uint16_t rms = _adc.readRxAudio();
    uint16_t th = 200 + (uint16_t)_s.squelch * 100;            // bring-up: порог TBD
    bool open = rms > th;
    digitalWrite(PIN_MUTE, open ? LOW : HIGH);
}

// ===== Обработчики состояний =====

void App::_processVfoInput() {
    int16_t enc = _enc.readDelta();
    BtnEvent eEnc = _enc.button().event();
    BtnEvent eUp = _btnUp.event();
    BtnEvent eDown = _btnDown.event();
    BtnEvent eLeft = _btnLeft.event();
    BtnEvent eRight = _btnRight.event();
    BtnEvent ePush = _btnPush.event();
    BtnEvent eRit = _btnRit.event();

    if (enc) {
        uint32_t step = (_s.step == 0) ? STEP_5K_HZ : STEP_10K_HZ;
        _stepFrequency(enc > 0 ? (int32_t)step : -(int32_t)step);
    }
    if (eEnc == BtnEvent::CLICK) { _s.step = (_s.step == 0) ? 1 : 0; _eeprom.save(_s); _dirty = true; }
    if (eEnc == BtnEvent::LONG)  { _enterMenu(); }

    if (eUp == BtnEvent::CLICK)   _stepChannel(+1);
    if (eDown == BtnEvent::CLICK) _stepChannel(-1);

    if (eLeft == BtnEvent::CLICK || eRight == BtnEvent::CLICK) {
        _s.mode = (_s.mode == 0) ? 1 : 0;
        _applyMode(); _freqDirty = true; _eeprom.save(_s); _dirty = true;
    }
    if (ePush == BtnEvent::CLICK) _enterMenu();

    if (eRit == BtnEvent::CLICK) {
        if (_s.mode == 0) { // RIT только в SSB
            _ritActive = !_ritActive;
            _state = _ritActive ? AppState::RIT : AppState::VFO;
            _dirty = true;
        }
    }
    if (eRit == BtnEvent::DOUBLE) {
        _setRit(0);
        _ritActive = false;
        _state = AppState::VFO;
        _eeprom.save(_s);
        _dirty = true;
    }
}

void App::_enterMenu() {
    _menuSel = 0;
    _menuEditing = false;
    _lastActivity = millis();
    _state = AppState::MENU;
    _dirty = true;
}

void App::_processMenuInput() {
    int16_t enc = _enc.readDelta();
    BtnEvent eEnc = _enc.button().event();
    BtnEvent eUp = _btnUp.event();
    BtnEvent eDown = _btnDown.event();
    BtnEvent eLeft = _btnLeft.event();
    BtnEvent eRight = _btnRight.event();
    BtnEvent ePush = _btnPush.event();

    if (enc || eEnc != BtnEvent::NONE || eUp != BtnEvent::NONE || eDown != BtnEvent::NONE ||
        eLeft != BtnEvent::NONE || eRight != BtnEvent::NONE || ePush != BtnEvent::NONE) {
        _lastActivity = millis();
    }

    if (!_menuEditing) {
        int8_t dir = 0;
        if (enc > 0) dir = +1; else if (enc < 0) dir = -1;
        if (eUp == BtnEvent::CLICK) dir = -1;
        if (eDown == BtnEvent::CLICK) dir = +1;
        if (dir) {
            if (dir > 0 && _menuSel < MENU_COUNT - 1) _menuSel++;
            if (dir < 0 && _menuSel > 0) _menuSel--;
            _dirty = true;
        }

        if (eEnc == BtnEvent::CLICK || ePush == BtnEvent::CLICK) {
            if (_menuSel == MENU_COUNT - 1) { // Factory reset
                _eeprom.factory(_s);
                _channel = _s.channel;
                _rfHz = channelFreq((uint8_t)_channel, _s.grid == 0);
                _ritHz = _s.ritHz;
                _applyMode();
                _display.setBacklight(_s.brightness);
                _freqDirty = true;
            } else {
                _menuEditing = true;
            }
            _dirty = true;
        }

        if (eEnc == BtnEvent::LONG || ePush == BtnEvent::LONG) {
            _state = AppState::VFO; _dirty = true;
        }
    } else {
        int8_t dir = 0;
        if (enc > 0) dir = +1; else if (enc < 0) dir = -1;
        if (eLeft == BtnEvent::CLICK) dir = -1;
        if (eRight == BtnEvent::CLICK) dir = +1;
        if (dir) { _menuAction(_menuSel, dir); _dirty = true; }

        if (eEnc == BtnEvent::CLICK || ePush == BtnEvent::CLICK) { _menuEditing = false; _dirty = true; }
        if (eEnc == BtnEvent::LONG || ePush == BtnEvent::LONG) {
            _menuEditing = false; _state = AppState::VFO; _dirty = true;
        }
    }

    if (millis() - _lastActivity >= MENU_TIMEOUT_MS) {
        _menuEditing = false; _state = AppState::VFO; _dirty = true;
    }
}

void App::_menuAction(uint8_t idx, int8_t dir) {
    switch (idx) {
        case 0: // Grid
            _s.grid = (_s.grid == 0) ? 1 : 0;
            _rfHz = channelFreq((uint8_t)_channel, _s.grid == 0);
            break;
        case 1: // Step
            _s.step = (_s.step == 0) ? 1 : 0;
            break;
        case 2: // Mode
            _s.mode = (_s.mode == 0) ? 1 : 0;
            _applyMode();
            _freqDirty = true;
            break;
        case 3: // Squelch
            _s.squelch = (uint8_t)constrain((int)_s.squelch + dir, 0, 9);
            break;
        case 4: // RIT step
            _s.ritStep = (_s.ritStep == 0) ? 1 : 0;
            break;
        case 5: // RIT auto-reset
            _s.ritAutoreset = (_s.ritAutoreset == 0) ? 1 : 0;
            break;
        case 6: // Backlight
            _s.brightness = (uint8_t)constrain((int)_s.brightness + dir * 10, 0, 100);
            _display.setBacklight(_s.brightness);
            break;
        case 7: // Factory reset — обрабатывается отдельно
        default:
            break;
    }
    _eeprom.save(_s);
    _dirty = true;
}

void App::_processRitInput() {
    int16_t enc = _enc.readDelta();
    BtnEvent eRit = _btnRit.event();
    BtnEvent eUp = _btnUp.event();
    BtnEvent eDown = _btnDown.event();

    if (enc) {
        uint32_t step = (_s.ritStep == 0) ? RIT_STEP_FINE_HZ : RIT_STEP_COARSE_HZ;
        _setRit(_ritHz + (enc > 0 ? (int32_t)step : -(int32_t)step));
    }

    if (eRit == BtnEvent::CLICK) {
        _ritActive = false; _state = AppState::VFO; _eeprom.save(_s); _dirty = true;
    }
    if (eRit == BtnEvent::DOUBLE) {
        _setRit(0); _ritActive = false; _state = AppState::VFO; _eeprom.save(_s); _dirty = true;
    }

    if (eUp == BtnEvent::CLICK || eDown == BtnEvent::CLICK) {
        if (eUp == BtnEvent::CLICK) _stepChannel(+1);
        if (eDown == BtnEvent::CLICK) _stepChannel(-1);
        if (_s.ritAutoreset) _setRit(0);
        _ritActive = false;
        _state = AppState::VFO;
        _dirty = true;
    }
}
