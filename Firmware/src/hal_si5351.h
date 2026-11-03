#pragma once
#include <Arduino.h>

// Обёртка над Adafruit Si5351: CLK0 = VFO, CLK1 = BFO.
class Si5351Synth {
public:
    bool begin();                 // Wire + PLL + выходы
    void setVfo(uint32_t hz);     // CLK0
    void setBfo(uint32_t hz);     // CLK1
    void enableOutputs(bool en);
    bool ok() const { return _ok; }

private:
    bool _ok = false;
};
