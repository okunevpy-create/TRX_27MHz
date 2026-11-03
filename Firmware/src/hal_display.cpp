#include "hal_display.h"
#include "pins.h"

bool Display::begin() {
    // SPI1 (по умолчанию у STM32F411: SCK=PA5, MOSI=PA7). DC=PA6, CS=PA4 — GPIO.
    // PA6 = DC, но у SPI1 это же MISO по умолчанию. ST7789 — write-only
    // (дисплей ничего не возвращает), поэтому MISO отключаем, освобождая PA6 под DC.
    SPI.setSCLK(PIN_LCD_SCK);
    SPI.setMOSI(PIN_LCD_MOSI);
    SPI.setMISO(PNUM_NOT_DEFINED); // снять MISO с PA6 (иначе конфликт с DC)
    _bus = new Arduino_HWSPI(PIN_LCD_DC, PIN_LCD_CS, &SPI);
    // ST7789 240×320, IPS, rotation 1 → landscape 320×240.
    _gfx = new Arduino_ST7789(_bus, PIN_LCD_RST, 1 /* rotation */, true /* ips */);
    _gfx->begin();
    _gfx->fillScreen(RGB565_BLACK);
    setBacklight(80);
    return true;
}

void Display::setBacklight(uint8_t pct) {
    // active-low: PB0 LOW = подсветка горит → PWM инвертируем.
    if (pct > 100) pct = 100;
    uint8_t duty = map(pct, 0, 100, 0, 255);
    analogWrite(PIN_LCD_BL, 255 - duty);
}

void Display::bar(int16_t x, int16_t y, int16_t w, int16_t h, float frac,
                  uint16_t color, uint16_t bg) {
    if (frac < 0) frac = 0;
    if (frac > 1) frac = 1;
    _gfx->fillRect(x, y, w, h, bg);
    _gfx->fillRect(x, y, (int16_t)(w * frac), h, color);
    _gfx->drawRect(x - 1, y - 1, w + 2, h + 2, RGB565_WHITE);
}
