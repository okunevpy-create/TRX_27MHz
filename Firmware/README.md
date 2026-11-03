# Прошивка

PlatformIO-проект для **STM32F411CEU6 (тактирование от HSI, без HSE)**.

## Статус

PlatformIO настроен, UI/UX **согласован** (`docs/firmware_ui_ux.md`).
**Скелет прошивки реализован и собирается** (`pio run` → SUCCESS, RAM ~4 % / Flash ~15 %).

## Сборка

```bash
pio run
pio run -t upload
pio device monitor
```

> Требуется PlatformIO CLI (`pio`). Board — **`genericSTM32F411CE`** (HSI 16 МГц →
> PLL → 96 МГц SYSCLK + 48 МГц USB). HSE 25 МГц BlackPill **не используется**.
> `upload_protocol = dfu`.

## Структура

- `src/main.cpp` — setup/loop, глюк.
- `src/app.{h,cpp}` — состояние (BOOT/VFO/TX/MENU/RIT), частота/канал/RIT, squelch, PTT, MODE, ограничитель.
- `src/ui.{h,cpp}` — отрисовка экранов (ST7789 через `Display`).
- `src/inputs.{h,cpp}` — `Button` (антидребезг + click/double/long) и `Encoder` (квадратура + кнопка).
- `src/hal_si5351.{h,cpp}` — Si5351 (CLK0=VFO, CLK1=BFO).
- `src/hal_display.{h,cpp}` — ST7789 (Arduino_GFX).
- `src/hal_adc.{h,cpp}` — ADC I_sense/SWR/RX_audio.
- `src/hal_eeprom.{h,cpp}` — AT24C02C (настройки).
- `include/pins.h` — маппинг GPIO (единая точка истины).
- `include/config.h` — константы + `Settings`.

## Маппинг GPIO

См. `include/pins.h` (источник: `docs/bom/stage1_control.md` §1.5).

## Ключевые примечания (bring-up)

- **Si5351 (Adafruit v1.6.0)**: библиотека жёстко считает опору **25 МГц**, а у нас
  **TCXO 27.6 МГц**. Поэтому делители считаются сами через низкоуровневые
  `setupPLL()/setupMultisynth()/setupRdiv()` с реальной опорой
  `SI5351_REF_HZ = 27.6 МГц` (без масштабирования). Проверить/откалибровать на
  bring-up (`docs/firmware_ui_ux.md` §12.1).
- **Дисплей PA6**: PA6 = `DC`, но у SPI1 это же `MISO` по умолчанию. Дисплею MISO не
  нужен — уже отключено в коде: `SPI.setMISO(PNUM_NOT_DEFINED)` в `hal_display.cpp`
  (`docs/firmware_ui_ux.md` §12.6).
- Пороги squelch, калибровка мощности/КСВ, направление энкодера — bring-up (§12.2–12.3).

## Тесты (native + Unity)

Юнит-тесты чистой логики (каналы/энкодер/кнопки) без железа:

```bash
pio test -e native
```

- Тестовый модуль: `test/test_logic.cpp`; шам `Arduino.h` — в `test/support/`.
- Чистая логика каналов вынесена в `include/channels.h` (header-only, без Arduino).
- **Требуется хостовый компилятор C/C++** (gcc/g++/clang/MSVC). На Windows это
  MinGW-w64: `winget install -e --id BrechtSanders.WinLibs.POSIX.UCRT`.

## Дизайн

- **UI/UX** — `docs/firmware_ui_ux.md` (экраны, состояния, меню, управление).
- **Каналы** — CEPT 40 (EU) + RUS (−5 кГц), таблица в `app.cpp`.

## Запланированные функции

- Управление Si5351 (VFO, BFO) по I²C (PB6/PB7). ✅ скелет
- Дисплей ST7789 240×320 (SPI1 + GPIO, подсветка PWM PB0). ✅ скелет
- UI: частота/канал/сетка, энкодер, джойстик, меню, память каналов (EU/RUS). ✅ скелет
- MODE (0=SSB / 1=AM) — PB9. ✅
- RIT (расстройка SSB) — энкодер + кнопка, EEPROM AT24C02C. ✅ скелет
- Squelch (программный, ADC PA2 RX_audio + MUTE PB8). ✅ скелет
- Ограничитель AM (PWR_LIMIT_SW PA11, PWR_LIMIT_EN PB10). ✅ скелет
- Защита по току/КСВ (I_sense PA0, SWR_sense PA1). ✅ скелет (заглушка калибровки)
