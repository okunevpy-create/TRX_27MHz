# Прошивка

PlatformIO-проект для **STM32F411CEU6 (тактирование от HSI, без HSE)**.

## Статус

PlatformIO настроен, UI/UX **согласован** (`docs/firmware_ui_ux.md`).
Код — заготовка (`src/main.cpp`), реализация — в следующих сессиях.
Предварительные испытания и отладка — через **Wokwi Simulator**.

## Сборка

```bash
pio run
pio run -t upload
pio device monitor
```

> Требуется PlatformIO CLI (`pio`). Board — **`genericSTM32F411CE`** (HSI 16 МГц →
> PLL → 96 МГц SYSCLK + 48 МГц USB). HSE 25 МГц BlackPill **не используется**
> (отказ в пользу встроенного HSI). `upload_protocol = dfu`.

## Структура

- `src/` — исходники (main.cpp)
- `include/` — заголовки
- `lib/` — локальные библиотеки PlatformIO
- `test/` — тесты

## Дизайн

- **UI/UX** — `docs/firmware_ui_ux.md` (экраны, состояния, меню, управление).
- **Маппинг GPIO** — `docs/bom/stage1_control.md` §1.4/§1.5.

## Запланированные функции

- Управление Si5351 (VFO, BFO) по I²C (PB6/PB7).
- Дисплей ST7789 240×320 (SPI1: PA5/PA7 + PA4/PA6/PA3/PB0, подсветка PB0).
- UI: частота/канал/сетка, энкодер, джойстик, меню, память каналов (EU/RUS).
- MODE (0=SSB / 1=AM) — PB9.
- RIT (расстройка SSB) — энкодер + кнопка, EEPROM AT24C02C.
- Squelch (программный, ADC PA2 RX_audio + MUTE PB8).
- Ограничитель AM (PWR_LIMIT_SW PA11, PWR_LIMIT_EN PB10).
- Защита по току/КСВ (I_sense PA0, SWR_sense PA1).
