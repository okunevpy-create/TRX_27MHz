#pragma once
#include <Arduino.h>
#include "config.h"

class Eeprom {
public:
    void begin();
    bool load(Settings& s);       // true = корректная запись
    void save(const Settings& s);
    void factory(Settings& s);    // дефолт + записать
private:
    void _writeByte(uint8_t addr, uint8_t v);
    uint8_t _readByte(uint8_t addr);
    void _write(const uint8_t* p, size_t n);
    void _read(uint8_t* p, size_t n);
};
