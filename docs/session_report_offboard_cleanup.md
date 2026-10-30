# Отчёт сессии — off-board wiring cleanup + LIMIT/FULL (2026-10-30)

## Цель
Разнести межплатные соединения на отдельные разъёмы (витая пара вместо «болтающихся» проводов) и перевести панельный тумблер LIMIT/FULL на логический SPDT с выбором напряжения затвора на плате.

## Сделано

### 1. Разбивка `J_PA_CTRL_1` (6P → 4P) + отдельные датчики
- `J_PA_CTRL_1` теперь 4P: **1=GND, 2=PTT, 3=PWR_LIMIT_EN, 4=PWR_LIMIT_SW** (на обеих платах).
- Добавлены отдельные 2P разъёмы под витую пару:
  - `J_I_SENSE_1`: 1=I_sense, 2=GND.
  - `J_SWR_1`: 1=SWR_sense, 2=GND.
- В `02_power_amp` разъёмы на базе `Connector:Conn_01x0N_Pin` + `JST_XH_B*B`; в `01_control` — `Connector_Generic:Conn_01x0N` + `JST_XH_B*B`.

### 2. LIMIT/FULL — SPDT `ASW-14-102` + MOSFET на плате
- Панельный тумблер заменён на **`ASW-14-102`** (SPDT ON-ON 3P, 20A 12VDC) — только логика, аналоговый `VGG` с платы не уходит.
- `J_SW_1` на `02_power_amp`: 6P→3P, пины **1=`PWR_LIMIT_SW`, 2=`PLIM_LIM`, 3=`GND`**.
- На плате: **Q5 (2N7002)** — G=`PWR_LIMIT_SW`, D=`VGG`, S=`VGG_LIMIT`; **R19 (100k)** `VGG_FULL`↔`VGG`.
- Выбор предела остаётся подстроечником `RV1` на `VGG_LIMIT` / `VGG_FULL`.

### 3. Итоговые цепи (проверено)
- `VGG` = C5:1, Q3:3, Q5:3, R19:2, R3:1, R4:1.
- `VGG_FULL` = R19:1, R5:2, R6:1, RV1:1.
- `VGG_LIMIT` = Q3:2, Q5:2, RV1:2.
- `PWR_LIMIT_SW` = D2:2, J_PA_CTRL_1:4, J_SW_1:1, Q5:1.
- `01_control`: `I_sense`=J_I_SENSE_1:1,U4:10; `SWR_sense`=J_SWR_1:1,U4:11; `PWR_LIMIT_EN`=J_PA_CTRL_1:3,U4:21; `PWR_LIMIT_SW`=J_PA_CTRL_1:4,U4:32.

## Проверки
- **`02_power_amp`:** ERC = 0 нарушений (PASS).
- **`01_control`:** ERC = 0 err / 7 warn — все `footprint_link_issues` (baseline, excluded; не преследовать).

## Область видимости меток
- Межплатные (global): `I_sense`, `SWR_sense`, `PTT`, `PWR_LIMIT_EN`, `PWR_LIMIT_SW`.
- Внутриплатные (local): `VGG`, `VGG_LIMIT`, `VGG_FULL`, `PLIM_LIM`.
- GND — через символ питания.

## Коммиты
- `f7c2e9e` — docs/contract/BOM sync.
- `b15a644` — `hw: J_PA_CTRL_1 4P и LIMIT/FULL SPDT в 02_power_amp` (ERC = 0).
- `8bccf85` — `hw: разбить J_PA_CTRL_1 в 01_control (4P + J_I_SENSE_1/J_SWR_1)`.

## Следующий шаг
Ревью схем 1+2 в GUI KiCad → переход к PCB (этапы 1 и 2 готовы к PCB).
