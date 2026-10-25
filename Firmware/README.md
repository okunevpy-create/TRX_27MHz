# Прошивка

PlatformIO-проект для STM32F411CEU6 (BlackPill).

## Статус
Заготовка. Текущий этап — **0** (мастер-лист).

## Сборка
```bash
pio run
pio run -t upload
pio device monitor
```

## Структура
- `src/` — исходники (main.cpp)
- `include/` — заголовки
- `lib/` — локальные библиотеки PlatformIO
- `test/` — тесты

## Запланированные функции
- Управление Si5351 (VFO, BFO, квадратура).
- UI: OLED, энкодер, меню, память каналов (EU/RUS).
- RIT (расстройка SSB).
- Squelch (программный, по ADC).
- Ограничитель AM (чтение PWR_LIMIT_SW, управление PWR_LIMIT_EN).
- Защита по току/КСВ.