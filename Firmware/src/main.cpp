// TRX 27 MHz — плата управления (01_control)
// STM32F411CEU6 (HSI 16 МГц → PLL → 96 МГц), PlatformIO.

#include <Arduino.h>
#include "app.h"

static App app;

void setup() {
    Serial.begin(115200); // USB CDC
    app.begin();
}

void loop() {
    app.run();
    delay(1);
}
