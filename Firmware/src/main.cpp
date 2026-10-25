// TRX 27 MHz — плата управления
// Этап 1: STM32F411 + Si5351 + DC-DC + защита
// TODO: реализовать в сессиях этапа 1

#include <Arduino.h>

void setup() {
    Serial.begin(115200);
    Serial.println("TRX 27MHz control board - boot");
}

void loop() {
    delay(1000);
}