#pragma once
#include <Arduino.h>
#include <Arduino_GFX_Library.h>

// Обёртка над Arduino_GFX ST7789 240×320 (landscape 320×240).
class Display {
public:
    bool begin();
    void setBacklight(uint8_t pct);       // 0..100 (PWM, active-low ключ)

    void clear(uint16_t color = RGB565_BLACK) { _gfx->fillScreen(color); }

    void setText(uint16_t color, uint8_t size) {
        _gfx->setTextColor(color);
        _gfx->setTextSize(size);
    }

    void text(int16_t x, int16_t y, const char* s) {
        _gfx->setCursor(x, y);
        _gfx->print(s);
    }

    void bar(int16_t x, int16_t y, int16_t w, int16_t h, float frac,
             uint16_t color, uint16_t bg);

    uint16_t width()  const { return 320; }
    uint16_t height() const { return 240; }

    Arduino_GFX* gfx() { return _gfx; }

private:
    Arduino_DataBus* _bus = nullptr;
    Arduino_GFX*     _gfx = nullptr;
};
