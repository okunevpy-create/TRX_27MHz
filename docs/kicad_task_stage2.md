# ТЗ для KiCad-сессии: схемотехника `02_power_amp` (этап 2, подэтапы 2.1–2.3)

> **Для кого:** отдельная сессия агента с доступом к KiCad MCP.
> **Источник правды по составу:** [`docs/bom/stage2_power_amp.md`](../bom/stage2_power_amp.md).
> **Контракты (источник правды по интерфейсам):** [`docs/contracts/control_pa.md`](../contracts/control_pa.md) и [`docs/contracts/rxtx_pa.md`](../contracts/rxtx_pa.md).
> **Проектные расчёты:** [`docs/calculations/pa_stage2.md`](../calculations/pa_stage2.md), [`docs/calculations/lpf_27mhz.md`](../calculations/lpf_27mhz.md).
> **Состав проекта сейчас:** схемотехника **2.1–2.3 выполнена, ERC=0** (отчёт — `docs/session_report_stage2.md`). Контракты `control_pa.md` / `rxtx_pa.md` — **ЗАФИКСИРОВАНЫ**.
> **Статус выполнения:** ✅ 2.1 (push-pull УМ), ✅ 2.2 (ФНЧ), ✅ 2.3 (датчики + LIMIT/FULL + T/R + LED) — **ВЫПОЛНЕНЫ**. Осталось: **PCB (разводка) → изготовление (отдельный шаг).**

> **Правило:** правки `.kicad_sch` / `.kicad_pro` — ТОЛЬКО через MCP-инструменты KiCad. Не редактировать S-выражения текстом.

---

## 0. Подготовка

1. Проверить наличие `KiCad/02_power_amp/02_power_amp.kicad_pro` и `02_power_amp.kicad_sch`.
2. Открыть проект и файл схемы через MCP (`kicad_set_project` с `project_dir` + `sch_file`).
3. **Убедиться, что активен именно `02_power_amp`** (не `00_master`, не `01_control`, не `03_rx_tx`).
4. Работать последовательно: одна операция → проверка → следующая. Не запускать параллельные KiCad-вызовы.
5. Лист A3 (или A4 при нехватке места) — как в `01_control`.

**Библиотеки:** стандартные KiCad (`Device`, `Package_TO_SOT_THT`, `Connector`, `Connector_JST`, `Connector_PinHeader_2.54mm`, `Connector_Coaxial`, `Capacitor_SMD`, `Inductor_SMD`, `Inductor_THT`, `Transformer`, `Transformer_THT`, `Relay`, `Switch`, `Potentiometer_THT`, `Diode_SMD`, `Amplifier_Operational`, `Transistor_FET`) + кастомная `trx_custom`.

---

## 1. Кастомные символы/футпринты (создать до разводки)

| Компонент | Символ | Footprint | Примечание |
|-----------|--------|-----------|------------|
| RD16HHF1 (Q1, Q2) | `trx_custom:RD16HHF1` ✅ | `Package_TO_SOT_THT:TO-220-3_Vertical` (штатный) | MOSFET. **Цоколёвка НЕСТАНДАРТНАЯ: 1=GATE, 2=SOURCE, 3=DRAIN, 4=FIN(SOURCE)** (2=Source, 3=Drain, фланец=Source). ✅ **Символ создан, цоколёвка проверена** (1=G, 2=S, 3=D, 4=FIN(S)). |
| Трансформаторы T1/T2/T_swr | ✅ `Device:Transformer_1P_1S` (T1) / `Device:Transformer_SP_1S` (T2) / `Device:L` (T_swr) | ✅ `Transformer_THT:Transformer_Toroid_Horizontal_D14.0mm_Amidon-T50` (T1) / `Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical` (T2) / `Inductor_THT:L_Toroid_Vertical_L13.0mm_W6.5mm_P5.60mm` (T_swr) | бифилярные на BN-61-202 (бинокуляр); generic-пады, silkscreen декоративный. `Value` = название сердечника. |
| Реле K1 | `trx_custom:IM06GR` | `trx_custom:Relay_DPDT_AXICOM_IM06GR_GullWing` (кастомный, gull-wing) | **TE IM06GR (2-1462037-3)**, SMD gull-wing; цоколёвка 1–8 по даташиту §Terminal assignment |
| Тумблер SW1 | `Switch:SW_DPDT` | **на панели (корпус)**; на плате — разъём `J_SW_1` (XH2.54 6-pin) ✅ | LIMIT/FULL — **KN3(B)-202-A2** (ON-ON, DPDT 6P, 6A 250VAC), **заказан** |

> ✅ **Символ RD16HHF1 — создан, цоколёвка проверена:** **1=GATE, 2=SOURCE, 3=DRAIN, 4=FIN(SOURCE)** (вывод 2 = Source, вывод 3 = Drain, фланец = Source). Footprint `TO-220-3_Vertical` универсален; маппинг пинов задан в символе. Source = вывод 2 + фланец (FIN).

---

## 2. Подэтап 2.1 — Push-pull УМ (RD16HHF1 + трансформаторы) ✅ ВЫПОЛНЕНО

### Цепи
```
J_RF_TX_1 (SMA, вход TX_RF ~0.5 Вт, 50 Ом)
   → T1 (входной балун, 50 Ом → балансные затворы)
   → R_g1/R_g2 (4.7–10 Ом, 0603) → затворы Q1/Q2
Q1/Q2 (RD16HHF1): истоки → GND_PWR (общий), стоки → T2 (выходной балун)
T2: центр первички → L_rfc → +12V_PA
    вторичка → выход 50 Ом (на ФНЧ 2.2)
```

| Ref | Действие |
|-----|----------|
| Q1, Q2 | RD16HHF1, push-pull, истоки на GND (фланец=Source), стоки на первичку T2 |
| T1 | входной балун (BN-61-202), бифиляр, коэффициент — место под 1:1 / 4:1. Символ `Device:Transformer_1P_1S`, footprint `Transformer_THT:Transformer_Toroid_Horizontal_D14.0mm_Amidon-T50` (4 пада) |
| T2 | выходной балун (BN-61-202), центр первички = питание. Символ `Device:Transformer_SP_1S` (5 выв., первичка с отводом), footprint `Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical` (5 падов) |
| L_rfc | дроссель стока, 4–6 мкГн (T68-2). Символ `Device:L`, footprint `Inductor_THT:L_Toroid_Vertical_L17.8mm_W8.1mm_P7.62mm_Bourns_5700` |
| R_g1, R_g2 | затворные 4.7–10 Ом (антипаразитные) |
| R_fb1, R_fb2 | (опц.) ОС 100–220 Ом, место зарезервировать |
| C_rf_d | 100 нФ развязка стоков ×2 |
| C_bulk_pa | 470 мкФ/25 В SMD (`CP_Elec_10x10.5`, уточнить по факту детали) |
| C_pa_byp | 10 мкФ (0805) + 100 нФ развязка +12V_PA |

> **Активный драйвер — НЕ ставим** (расчёт: 0.5 Вт раскачки достаточно, запас +2.2 дБ), но зарезервировать место/пады (не монтировать).

---

## 3. Подэтап 2.2 — ФНЧ 27 МГц (5-й порядок) ✅ ВЫПОЛНЕНО

Топология (лестница, 50 Ом): **C–L–C–L–C**.

| Ref | Значение | Примечание |
|-----|----------|------------|
| C_lpf1 | 120 пФ C0G 100 В, 0805 (0805N121G101CT) | вход ФНЧ (после T2) |
| L_lpf1 | 360 нГн (T50-6, ~10 витков). `Device:L` + `Inductor_THT:L_Toroid_Vertical_L13.0mm_W6.5mm_P5.60mm` | |
| C_lpf2 | 220 пФ C0G 100 В, 0805 (CC0805JRNPO0BN221) | |
| L_lpf2 | 360 нГн (T50-6). `Device:L` + `Inductor_THT:L_Toroid_Vertical_L13.0mm_W6.5mm_P5.60mm` | |
| C_lpf3 | 120 пФ C0G 100 В, 0805 (0805N121G101CT) | выход ФНЧ (на T/R) |

> Выход ФНЧ → контакт реле K1 (TX-сторона). Вход ФНЧ — от T2 (выходной балун).

---

## 4. Подэтап 2.3 — Датчики + LIMIT/FULL + смещение + T/R (БЛОКИРУЮЩИЙ) ✅ ВЫПОЛНЕНО

> Разводится **совместно с 1.5** (контракт `control_pa.md` уже зафиксирован). До завершения 2.3 плату этапа 1 не травить.

### 4.1 Разъёмы интерфейса (по контракту `control_pa.md`)
| Разъём | Пин | Сигнал |
|--------|-----|--------|
| J_PA_CTRL_1 (XH2.54 6P) | 1 | GND |
| | 2 | PTT |
| | 3 | PWR_LIMIT_EN |
| | 4 | PWR_LIMIT_SW |
| | 5 | I_sense |
| | 6 | SWR_sense |
| J_PA_PWR_1 (клеммник 2P 5.0 мм) | 1 | +12V_PA |
| | 2 | GND |

### 4.2 Смещение + LIMIT/FULL
```
+12V_PA → делитель Vgg (с опц. NTC/диодом) → SW1 (полюс A):
   LIMIT → RV1 (подстроечник) → узел Vgg → R_g1/R_g2 → затворы
   FULL  → полный Vgg → узел Vgg → затворы
PWR_LIMIT_EN (3.3 В, active-high) → Q_lim (2N7002) → принудительно RV1 (LIMIT)
LED D_lim + R_led → горит при (LIMIT ИЛИ PWR_LIMIT_EN)
PWR_LIMIT_SW ← делитель 27к/10к от +12 В, переключается SW1 (полюс B): LIMIT=3.3 В, FULL=0 В
```

| Ref | Действие |
|-----|----------|
| SW1 | DPDT: полюс A = смещение (RV1 vs полный Vgg), полюс B = PWR_LIMIT_SW. **Монтируется на панель**; на плате — разъём `J_SW_1` (XH2.54 6-pin, пины ниже) |
| RV1 | подстроечник 3296W 10к (калибровка 4 Вт) |
| D_lim + R_led | светодиод LIMIT + резистор 1–2.2 к |
| Q_lim | 2N7002, ключ PWR_LIMIT_EN |
| R_lim_pu/pd | 27к / 10к делитель PWR_LIMIT_SW |

> **`J_SW_1` (XH2.54 6-pin) — разъём панельного тумблера SW1.** Пины: 1=`VGG` (полюс A общий → затворы), 2=`VGG_LIMIT` (RV1), 3=`VGG_FULL` (полное смещение), 4=`PWR_LIMIT_SW` (полюс B общий), 5=`PLIM_LIM` (+12В через R_lim_pu 27к), 6=`GND` (полюс B FULL).

### 4.3 T/R реле
```
PTT (3.3 В) → Q_ptt (2N7002/MMBT3904) → катушка K1 (12 В) + D_rel (1N4148WS, обратный)
K1: COM → J_ANT_1 (антенна)
    NO (TX) → выход ФНЧ
    NC (RX) → J_RF_RX_1 (на 03_rx_tx)
```

| Ref | Действие |
|-----|----------|
| K1 | **TE IM06GR (2-1462037-3)** — DPDT 12 В, SMD gull-wing. COM→J_ANT_1, NO→ФНЧ(TX), NC→RX_RF |
| Q_ptt | ключ реле |
| D_rel | обратный диод 1N4148WS (SOD-323) |

### 4.4 Датчики
| Ref | Действие |
|-----|----------|
| R_shunt | 0.05 Ом 1%/2 Вт (Yageo PA2512FKE7W0R05E) в шине +12V_PA → U_sense (LM358, single 12 В) → I_sense (0–3.3 В) |
| U_sense | LM358, усиление ~22, выход делитель/ограничение ≤3.3 В |
| T_swr | трансформатор тока BN-61-202 (мост Стоктона) на линии J_ANT_1. Символ `Device:L` (2 выв.), footprint `Inductor_THT:L_Toroid_Vertical_L13.0mm_W6.5mm_P5.60mm` |
| D_swr | BAT54 ×2, детектор → SWR_sense (0–3.3 В) |

### 4.5 Отладочные светодиоды (дублирующий LIM + power-good)
> См. `docs/led_debug_scheme.md` и BOM `stage2_power_amp.md` §2.5.

| Ref | Действие |
|-----|----------|
| D_lim_b + R_led_b (2.2 кОм) | платный дубль LIM: узел «LIMIT активен» → R_led_b → D_lim_b (0805 красный) → GND |
| D_pa_pwr + R_pa_pwr (3.3 кОм) | power-good: `+12V_PA` → R_pa_pwr → D_pa_pwr (0805 зелёный) → GND |

> Панельный LIM (`D_lim`, 3 мм, DEFERRED) — через `J_LIM_LED_1` (2-pin) + `R_led` (§2.3). `D_lim_b`/`D_pa_pwr` — на тех же существующих узлах (LIMIT, `+12V_PA`), новых межблочных сигналов нет.

---

## 5. Новые цепи (появившиеся после 2.1–2.3)

| Цепь | Откуда | Куда |
|------|--------|------|
| `TX_RF` | J_RF_TX_1 (вход) | T1 (входной балун) |
| `+12V_PA` | J_PA_PWR_1:1 | L_rfc (стоки), делитель Vgg, шунт I_sense |
| `GND` / `GND_PWR` | J_PA_PWR_1:2 / J_PA_CTRL_1:1 | истоки, экран, общая точка |
| `PTT` | J_PA_CTRL_1:2 | Q_ptt (ключ реле) |
| `PWR_LIMIT_EN` | J_PA_CTRL_1:3 | Q_lim |
| `PWR_LIMIT_SW` | делитель/SW1 | J_PA_CTRL_1:4 |
| `VGG` / `VGG_LIMIT` / `VGG_FULL` | J_SW_1 (полюс A: 1/2/3) | узел смещения затворов / RV1 / полный Vgg |
| `PLIM_LIM` | J_SW_1:5 | R_lim_pu (27к → +12В) |
| `I_sense` | U_sense | J_PA_CTRL_1:5 |
| `SWR_sense` | D_swr | J_PA_CTRL_1:6 |
| `RX_RF` | K1 (NC) | J_RF_RX_1 (выход на 03_rx_tx) |
| `ANT` | K1 (COM) | J_ANT_1 (BNC, задняя крышка) |

---

## 6. Критерии готовности (Definition of Done)

- [x] 2.1–2.3 разведены; каждое изменение подтверждено повторным чтением через MCP.
- [x] Разъёмы J_PA_CTRL_1 / J_PA_PWR_1 — по контракту `control_pa.md` (пинаут сверен).
- [x] Разъём `J_SW_1` (XH2.54 6-pin) — разведён по пинауту §4.2 (1=`VGG`, 2=`VGG_LIMIT`, 3=`VGG_FULL`, 4=`PWR_LIMIT_SW`, 5=`PLIM_LIM`, 6=`GND`).
- [x] ВЧ-разъёмы J_RF_TX_1 / J_RF_RX_1 / J_ANT_1 — по контракту `rxtx_pa.md`.
- [x] Логика LIMIT/FULL + PWR_LIMIT_EN + PWR_LIMIT_SW + LED — соответствует `docs/calculations/pa_stage2.md` §3.
- [x] Отладочные LED (§4.5): `D_lim_b`+`R_led_b`, `D_pa_pwr`+`R_pa_pwr` — разведены, на корректных узлах (LIMIT / `+12V_PA`), без новых межблочных сигналов.
- [x] ERC: нет **новых** `pin_to_pin` / `multiple_net_names` / `power_pin_not_driven`. Допустимы `Pin not connected` у NC и (до стыковки с этапом 3) изолированные `TX_RF`/`RX_RF`.
- [x] Неиспользуемые входы активных элементов — не в «воздухе».
- [x] Отчёт: таблица «ref → что сделано → отклонения», список выбранных футпринтов/символов, остаточные ERC.

---

## 7. Ограничения

- **Не менять имена межблочных сигналов** (`PTT`, `PWR_LIMIT_EN`, `PWR_LIMIT_SW`, `I_sense`, `SWR_sense`, `+12V_PA`, `TX_RF`, `RX_RF`) — зафиксированы в `docs/contracts/`.
- `00_master` не трогать. `01_control` в этой сессии не редактировать (2.3 стыкуется с 1.5 только по контракту).
- Кастомные символы/footprint'ы — **только** в `KiCad/libs/{symbols,footprints}`; генерация через MCP в `output` → `move` в `libs`.
