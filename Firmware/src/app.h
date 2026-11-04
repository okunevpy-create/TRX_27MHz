#pragma once
#include <Arduino.h>
#include "config.h"
#include "pins.h"
#include "inputs.h"
#include "hal_si5351.h"
#include "hal_display.h"
#include "hal_adc.h"
#include "hal_eeprom.h"
#include "ui.h"

enum class AppState : uint8_t { BOOT, VFO, TX, MENU, RIT };

class App {
public:
    void begin();
    void run();  // вызывать в loop()

    // ---- getters для UI ----
    AppState state() const { return _state; }
    uint32_t rfHz() const { return _rfHz; }
    uint16_t channel() const { return _channel; }
    bool gridEu() const { return _s.grid == 0; }
    Mode mode() const { return (Mode)_s.mode; }
    int32_t ritHz() const { return _ritHz; }
    uint8_t step() const { return _s.step; }
    uint8_t squelch() const { return _s.squelch; }
    uint8_t brightness() const { return _s.brightness; }
    bool limitSw() const { return _limitSw; }
    bool tx() const { return _ptt; }
    float powerW() const { return _powerW; }
    float swr() const { return _swr; }
    bool menuEditing() const { return _menuEditing; }
    uint8_t menuSel() const { return _menuSel; }
    const Settings& settings() const { return _s; }
    Display& display() { return _display; }

private:
    // modules
    Si5351Synth _synth;
    Display     _display;
    Adc         _adc;
    Eeprom      _eeprom;
    Encoder     _enc;
    Button      _btnUp, _btnDown, _btnLeft, _btnRight, _btnPush, _btnRit, _btnPtt;
    Ui          _ui;

    Settings  _s;
    AppState  _state = AppState::BOOT;
    uint32_t  _rfHz = 27135000UL;   // 27.135 МГц (CEPT ch15)
    uint16_t  _channel = 15;
    int32_t   _ritHz = 0;
    bool      _ritActive = false;
    bool      _ptt = false;
    bool      _limitSw = false;
    float     _powerW = 0;
    float     _swr = 1.0f;

    // menu
    uint8_t   _menuSel = 0;
    bool      _menuEditing = false;

    // timings
    uint32_t _bootMs = 0;
    uint32_t _lastSi = 0;
    uint32_t _lastSquelch = 0;
    uint32_t _lastAdc = 0;
    uint32_t _lastActivity = 0;
    uint32_t _lastRedraw = 0;
    bool     _dirty = true;
    bool     _freqDirty = true;

    void _applyFrequency();        // VFO = RF + IF (+RIT только в RX/SSB); BFO фикс.
    void _applyMode();
    void _applyPowerLimit();
    void _updateMeasurements();
    void _processSquelch();

    void _setChannel(uint16_t ch);
    void _stepChannel(int16_t dir);
    void _stepFrequency(int32_t hz);
    void _setRit(int32_t hz);
    void _enterTx();
    void _exitTx();

    void _processVfoInput();
    void _processMenuInput();
    void _processRitInput();
    void _enterMenu();
    void _menuAction(uint8_t idx, int8_t dir);

    uint32_t _vfoHz() const;
};
