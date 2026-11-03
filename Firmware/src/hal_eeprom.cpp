#include "hal_eeprom.h"
#include <Wire.h>

void Eeprom::begin() {
    Wire.begin(); // PB6/PB7 (I2C1), общая с Si5351
}

void Eeprom::_writeByte(uint8_t addr, uint8_t v) {
    Wire.beginTransmission(EEPROM_I2C_ADDR);
    Wire.write(addr);
    Wire.write(v);
    Wire.endTransmission();
    delay(5); // цикл записи AT24C02C
}

uint8_t Eeprom::_readByte(uint8_t addr) {
    Wire.beginTransmission(EEPROM_I2C_ADDR);
    Wire.write(addr);
    Wire.endTransmission(false);
    Wire.requestFrom((uint8_t)EEPROM_I2C_ADDR, (uint8_t)1);
    return Wire.available() ? (uint8_t)Wire.read() : 0xFFu;
}

void Eeprom::_write(const uint8_t* p, size_t n) {
    for (size_t i = 0; i < n; i++) _writeByte((uint8_t)i, p[i]);
}

void Eeprom::_read(uint8_t* p, size_t n) {
    for (size_t i = 0; i < n; i++) p[i] = _readByte((uint8_t)i);
}

bool Eeprom::load(Settings& s) {
    Settings tmp;
    _read((uint8_t*)&tmp, sizeof(tmp));
    if (tmp.magic == SETTINGS_MAGIC && tmp.version == SETTINGS_VERSION) {
        s = tmp;
        return true;
    }
    return false;
}

void Eeprom::save(const Settings& s) {
    _write((const uint8_t*)&s, sizeof(s));
}

void Eeprom::factory(Settings& s) {
    s = Settings{};
    save(s);
}
