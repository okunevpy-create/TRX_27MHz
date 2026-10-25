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
| +12V_PA | control → PA | защищённые, звёздой от входного узла control |
| GND | — | отдельная от сигнальной, соединение в одной точке |
| GND_SIG | — | сигнальная земля |

## Этап 1 (`01_control`) ↔ Этап 3 (`03_rx_tx`)
Контракт: [contracts/control_rxtx.md](contracts/control_rxtx.md)

| Сигнал | Направление | Примечание |
|--------|-------------|------------|
| VFO | control → rxtx | ~37,7 МГц, ~1 В pp, 50 Ом |
| BFO | control → rxtx | 10,7 МГц, ~1 В pp, 50 Ом |
| I | control → rxtx | квадратура 90°, ~0,5 В pp |
| Q | control → rxtx | квадратура 90°, ~0,5 В pp |
| RX_audio | rxtx → control | для squelch (ADC) |
| PTT | control → rxtx | 0/3,3 В |
| +12V_RXTX | control → rxtx | защищённые, звёздой от входного узла control |
| GND | — | сигнальная земля |

## Этап 2 (`02_power_amp`) ↔ Этап 3 (`03_rx_tx`) — ВЧ напрямую, минуя control
Контракт: [contracts/rxtx_pa.md](contracts/rxtx_pa.md)

| Сигнал | Направление | Примечание |
|--------|-------------|------------|
| TX_RF | rxtx → PA | ~0,5 Вт раскачки, 50 Ом, SMA |
| RX_RF | PA → rxtx | до 1 Вт просачивания, с T/R реле, защита на входе rxtx |
| GND | — | экран |

## Замечания по земле
На Этапе 0 (логическая схема) — один `GND` на всех листах. В реальных платах земля раздельная: `GND_DIG`, `GND_ANA`, `GND_PWR`, соединение — в одной точке на каждой плате.