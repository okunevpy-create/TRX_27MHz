# Сводная распиновка межмодульных разъёмов

> Детальные контракты — в `contracts/`.

## Этап 1 (`01_control`) ↔ Этап 2 (`02_power_amp`)
Контракт: [contracts/control_pa.md](contracts/control_pa.md)

| Сигнал | Направление | Примечание |
|--------|-------------|------------|
| PTT | control → PA | |
| I_sense | PA → control | аналоговый, с шунта |
| SWR_sense | PA → control | аналоговый, опционально |
| PWR_LIMIT_EN | control → PA | программное управление ограничителем |
| PWR_LIMIT_SW | PA → control | обратная связь: положение тумблера |
| RF in | rxtx → PA | ~0,5 Вт раскачки |
| +12 В | control → PA | защищённые, силовые |
| GND | — | силовая земля |

## Этап 1 (`01_control`) ↔ Этап 3 (`03_rx_tx`)
Контракт: [contracts/control_rxtx.md](contracts/control_rxtx.md)

| Сигнал | Направление | Примечание |
|--------|-------------|------------|
| VFO out | control → rxtx | ~37,7 МГц, ~1 В pp |
| BFO out | control → rxtx | 10,7 МГц |
| I/Q out | control → rxtx | квадратура 90° |
| RX_audio | rxtx → control | для squelch (ADC) |
| PTT | control → rxtx | |
| +12 В | control → rxtx | защищённые |
| GND | — | сигнальная земля |

## Этап 2 (`02_power_amp`) ↔ Этап 3 (`03_rx_tx`)
| Сигнал | Направление | Примечание |
|--------|-------------|------------|
| RX_in | PA → rxtx | с T/R реле, защита на входе rxtx |
| GND | — | экран |