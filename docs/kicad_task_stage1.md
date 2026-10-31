# ТЗ для KiCad-сессии: схемотехника `01_control` (этап 1, подэтапы 1.1–1.5)

> **Для кого:** отдельная сессия агента с доступом к KiCad MCP.
> **Источник правды по составу:** [`docs/bom/stage1_control.md`](../bom/stage1_control.md).
> **Контракты (источник правды по интерфейсам):** [`docs/contracts/control_pa.md`](../contracts/control_pa.md) и [`docs/contracts/control_rxtx.md`](../contracts/control_rxtx.md).
> **Состав проекта сейчас:** схемотехника **1.1–1.5 (control-часть) + read-only валидация выполнены**. ERC = **0 error / 7 warning** (все `footprint_link_issues`, все `excluded`). Контракт `control_pa.md` — **ЗАФИКСИРОВАН** (2026-10-28); `control_rxtx.md` — пинаут разъёмов зафиксирован.
> **Статус выполнения:** ✅ 1.1, ✅ 1.2, ✅ 1.3, ✅ 1.4, ✅ 1.5 (control-часть), ✅ F1–F13, ✅ read-only валидация — **ВЫПОЛНЕНЫ**. Осталось: **PCB (разводка) → изготовление (отдельный шаг этапа)**. **Травление платы этапа 1 РАЗБЛОКИРОВАНО** (1.5 + 2.3 + `control_pa.md` готовы).

> **Правило:** правки `.kicad_sch` / `.kicad_pro` — ТОЛЬКО через MCP-инструменты KiCad. Не редактировать S-выражения текстом.

---

## 0. Подготовка

1. Проверить наличие `KiCad/01_control/01_control.kicad_pro` и `01_control.kicad_sch`.
2. Открыть проект и файл схемы через MCP (`kicad_set_project` с `project_dir` + `sch_file`).
3. **Убедиться, что активен именно `01_control`** (не `00_master`, не `02_power_amp`, не `03_rx_tx`).
4. Работать последовательно: одна операция → проверка → следующая. Не запускать параллельные KiCad-вызовы.

**Библиотеки:** стандартные KiCad (`Device`, `Package_*`, `Connector`, `Connector_Generic`, `Connector_JST`, `Connector_PinHeader_2.54mm`, `TerminalBlock_Phoenix`, `Diode_SMD`, `Capacitor_SMD`, `Inductor_SMD`, `Oscillator`, `Amplifier_Operational`, `74xx`, `MCU_ST_STM32F4`, `Regulator_Switching`, `Transistor_FET`) + кастомная `trx_custom` (RT9193-33).

---

## 1. Исправления F1–F13 ✅ ВЫПОЛНЕНО

> Это **сверка схемы с реальным BOM** (`stage1_control.md`). Все F1–F13 выполнены; отклонения от исходного ТЗ зафиксированы ниже в столбце «Отклонение».

| # | Ref | Что сделано (факт, по `sch_get_symbols`) | Отклонение |
|---|-----|------------------------------------------|------------|
| F1 | U1 | LM2596S-5, footprint `Package_TO_SOT_SMD:TO-263-5_TabPin3` (было TO-263-3) | нет |
| F2 | U2, U3 | RT9193-33 (`trx_custom:RT9193-33`), footprint `Package_TO_SOT_SMD:SOT-23-5` (было AMS1117 SOT-223) | нет |
| F3 | U7 | LM358 (value `LM358DR`), **3 юнита** (unit A обвязан как MIC-предусилитель; unit B → GND/NC; unit 3 — питание). Footprint `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | ⚠️ исходное ТЗ: `…_HandSolder`; в KiCad **нет** HandSolder-варианта SOIC-8 → взят обычный (зафиксировано и на этапе 2) |
| F4 | U6 | ~~74HC74 (`74xx:74HC74`), 3 юнита~~ **УДАЛЁН** (квадратура — балласт, 2026-10-31) | нет |
| F5 | J_OLED_1/J_ENC_1/J_BTN_1/J_PA_CTRL_1/J_RXTX_SIG_1 | XH2.54: 8P/5P/**8P**/6P/10P (`Connector_JST:JST_XH_*_P2.50mm_Vertical`) | ⚠️ `J_BTN_1` **8 pin**, а не 7 (добавлен `BTN_RIT`); footprint XH имеет номинал шага `P2.50mm` |
| F5b | J_SWD_1, J_UART_1 | оставлены `PinHeader_2.54mm`: `PinHeader_1x05` (5P, с NRST) / `PinHeader_1x04` (4P) | нет (осознанное решение — удобство отладки) |
| F6 | J_PA_PWR_1, J_RXTX_PWR_1 | клеммник 2P 5.0 мм `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2_1x02_P5.00mm_Horizontal` | ≡ WJ127R-5.0-02P (функциональные эквиваленты) |
| F7 | U8 | 74AHC541 (`74xx:74AHC541`), footprint `Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm`; входы A3/A4/A5/A6/A7/A8→GND, `2OE`→GND | ⚠️ исходное ТЗ `74AC541`; **74AHC541** принят как совместимый (2026-10-29) |
| F8 | C1, C3 | C1 1000 мкФ/25 В → `Capacitor_SMD:CP_Elec_10x12.5`; C3 470 мкФ/16 В → `Capacitor_SMD:CP_Elec_8x10.5` | ⚠️ исходное ТЗ: C1 `12.5×13`, C3 `8×10.2`; уточнено по фактическим деталям |
| F9 | L2, L3 | `Device:FerriteBead`, значение **MMZ2012R601AT000** (600Ω@100МГц), footprint `Inductor_SMD:L_0805_2012Metric` | нет |
| F10 | R5, C21 | R5 = **10 Ом** (последовательно `+3V3_SI → R5 → +3V3_SI_F`), C21 = **1 мкФ** на `+3V3_SI_F` | нет |
| F11 | U9 + C26/C27/C28 | RT9193-33 (`trx_custom:RT9193-33`), `SOT-23-5`; C26=1 мкФ (IN), C27=10 мкФ (OUT), C28=10 нФ (BP); выход `+3V3_DISP` | нет |
| F12 | J_OLED_1 | 8-pin ST7789 (`Conn_01x08`), пинаут по модулю: 1=GND, 2=`+3V3_DISP`, 3=`OLED_SCK`, 4=`OLED_MOSI`, 5=`LCD_RST`, 6=`OLED_DC`, 7=`OLED_CS`, 8=`LCD_BLK` | нет |
| F13 | R6–R18, C29–C37 | RC-фильтры UI: R6–R14 = 10 кОм ×9 (кнопки+энкодер), C29–C37 = 100 нФ ×9, SPI-демпферы R15–R18 = 22 Ом ×4 (SCK/MOSI/CS/DC) | нет |

---

## 2. Подэтап 1.4 — UI / RIT / squelch / MIC ✅ ВЫПОЛНЕНО

> Отчёт: [`docs/session_report_1.4.md`](session_report_1.4.md). Лист увеличен до **A2 (594×420 мм)**.

| Ref | Значение | Назначение | Footprint |
|-----|----------|------------|-----------|
| R23 | 2.2 кОм | bias электрета (+3V3 → MIC+) | R_0603…HandSolder |
| R24 | 10 кОм | делитель смещения (верх, +3V3 → V+) | R_0603…HandSolder |
| R25 | 10 кОм | делитель смещения (низ, V+ → GND) | R_0603…HandSolder |
| R26 | 100 кОм | обратная связь (Vout → V−) | R_0603…HandSolder |
| R27 | 10 кОм | усиление (V− → C41 → GND) | R_0603…HandSolder |
| R28 | 1 кОм | RC-фильтр `RX_audio` | R_0603…HandSolder |
| C39 | 1 мкФ | входная связь (MIC+ → V+) | C_0603…HandSolder |
| C40 | 10 нФ | RC-фильтр `RX_audio` | C_0603…HandSolder |
| C41 | 10 мкФ | AC-земля в ОС (последовательно с R27) | C_0805…HandSolder |

- MIC-предусилитель: U7 unit A, неинвертирующий, K≈11 (DC gain=1); выход → `MIC_LINE` (глобальная метка).
- Squelch: `RX_audio` → R28 (1 кОм) → `RX_audio_F` + C40 (10 нФ) → GND; τ=10 мкс → ADC.
- RIT: цепи `BTN_RIT` (J_BTN_1:7), `ENC_*` (J_ENC_1) заведены через RC-фильтры; логика — в прошивке.

---

## 3. Подэтап 1.5 (control-часть) — GPIO + питание-звезда + буферы ✅ ВЫПОЛНЕНО

> Промт: [`docs/session_prompt_1.5.md`](session_prompt_1.5.md). Выполнялось совместно с 2.3 (контракт `control_pa.md`).

- **Питание-звезда:** `VIN_PROT` → R29 (0 Ом) → `+12V_PA`; `VIN_PROT` → R30 (0 Ом) → `+12V_RXTX`. R29/R30 = **0 Ом 1206** (`R_1206_3216Metric…HandSolder`).
- **Буферы VFO/BFO (U8 74AHC541):** выходы `VFO_OUT`/`BFO_OUT` через R19–R20 (22 Ом, 0603). Входы A5/A6 → GND, выходы Y5/Y6 → NC, `2OE` (U8:19) → GND.
- **NC** на неиспользуемые GPIO MCU; неиспользуемые входы U8 → GND.

### Привязка GPIO (MCU → сигнал)

| MCU | Сигнал | MCU | Сигнал | MCU | Сигнал |
|-----|--------|-----|--------|-----|--------|
| PA0 | `I_sense` | PB0 | `LCD_BLK` | PC13 | `BTN_UP` |
| PA1 | `SWR_sense` | PB1 | `BTN_RIGHT` | PC14 | `BTN_DOWN` |
| PA2 | `RX_audio_F` | PB2 | `BTN_PUSH` | PC15 | `BTN_LEFT` |
| PA3 | `LCD_RST` | PB5 | `PTT_IN` | | |
| PA4 | `SPI_CS` | PB8 | `MUTE` | | |
| PA5 | `SPI_SCK` | PB9 | `MODE` | | |
| PA6 | `SPI_DC` | PB10 | `PWR_LIMIT_EN` | | |
| PA7 | `SPI_MOSI` | PB12 | `BTN_RIT` | | |
| PA8 | `PTT` | PB13 | `ENC_CLK` | | |
| PA11 | `PWR_LIMIT_SW` | PB14 | `ENC_DT` | | |
| | | PB15 | `ENC_SW` | | |

> Полная таблица — `docs/bom/stage1_control.md` §1.5.

---

## 4. Read-only валидация + исправления ✅ ВЫПОЛНЕНО

> Валидация `01_control.kicad_sch` (read-only) — `docs/session_report_validation.md`; решения приняты пользователем 2026-10-29.

| Что | Исправление (факт) |
|-----|--------------------|
| Вход питания | добавлен **J_12V_IN_1** (клеммник 2P 5.0 мм, `+12V_IN`/GND) |
| F1 предохранитель | держатель **Keystone 3512P** (5×20, THT) — `Fuse:Fuseholder_Clip-5x20mm_Keystone_3512P_Inline_…` |
| VDDA | феррит **L4** (`+3V3`→VDDA, MMZ2012R601AT000; VDDA = U4:9 + C20 + C25) |
| TCXO Si5351 | **Y2 = TG2520SMN-27.6000M-MCGNNM3** (4-pin 2520) вместо `Device:Crystal`; развязка **C42=100 нФ** |
| Bulk входа U3 | добавлен **C43 = 1 мкФ** (0603) параллельно C8 на `+5V_SI` |
| SWD | **J_SWD_1** расширен 4→5 pin, pin5 = `NRST`; footprint `PinHeader_1x05_P2.54mm_Vertical` |
| PTT гарнитуры | добавлен **J_PTT_IN_1** (тест-пойнт) → R32 1к → R31 10к (pull-up +3V3) + C44 100 нФ → PB5 |
| Подсветка LCD | ключ **Q1 AO3401** + R33 100R + R34 100k + R35 12R: PB0→R33→Q1.G, Q1.S→`+3V3_DISP`, Q1.D→R35→`LCD_BL`→J_OLED_1:8 (active-low) |
| Отладочные LED | D4–D8 (0805) + R36–R42 (470R/1k) → J_LED_1 (3-pin) |
| `+5V` | power-символ `power:+5V` (устранён warning `single_global_label`) |
| Развязка +3V3 | добавлен **C38 = 100 нФ** |

### Финальный ERC

- **0 error / 7 warning** — все warning = `footprint_link_issues` (символы с «мягкой» привязкой footprint: J_12V_IN_1, J_PA_PWR_1, J_RXTX_PWR_1), все `excluded`.
- Реальных электрических нарушений (pin_to_pin / multiple_net_names / power_pin_not_driven) — **нет**.

---

## 5. Новые цепи (финальное состояние)

| Цепь | Откуда | Куда |
|------|--------|------|
| `+12V_IN` | J_12V_IN_1 | F1 → D1/D2 (защита) → `VIN_PROT` → U1 |
| `+5V` | U1 (LM2596) | U2, U3, U9 |
| `+3V3` | U2 | MCU, Si5351 (через L2), логика |
| `+3V3_SI` | U3 | R5 (10 Ом) → `+3V3_SI_F` → Si5351 |
| `+3V3_DISP` | U9 | J_OLED_1:2, Q1.S (подсветка) |
| `VDDA` | L4 (от +3V3) | U4:9 + C20 + C25 |
| `VFO_OUT`/`BFO_OUT` | U8 (буферы) | J_VFO_1/J_BFO_1 (межплатные) |
| `MIC_LINE` | U7 (LM358) | J_RXTX_SIG_1 (межблочная) |
| `RX_audio` | J_RXTX_SIG_1 | R28/C40 → `RX_audio_F` → ADC (PA2) |
| `PTT`, `I_sense`, `SWR_sense`, `PWR_LIMIT_EN`, `PWR_LIMIT_SW`, `MUTE` | межблочные (контракт `control_pa.md`) | GPIO MCU / J_PA_CTRL_1 |

---

## 6. Критерии готовности (Definition of Done)

- [x] F1–F13 выполнены; каждое изменение подтверждено повторным чтением через MCP.
- [x] 1.1–1.3 (защита/DC-DC/LDO, MCU+кварц+SWD+UART, Si5351) — разведены.
- [x] 1.4 (UI/RIT/squelch/MIC-предусилитель) — разведён (R23–R28, C39–C41).
- [x] 1.5 (GPIO-привязка + питание-звезда R29/R30 + буферы VFO/BFO) — разведён.
- [x] Все разъёмы `J_*` — **с индексом на конце** (`J_OLED_1`, `J_PA_CTRL_1`, …, `J_PTT_IN_1`); J_SWD_1/J_UART_1 оставлены PinHeader (осознанно).
- [x] Неиспользуемые входы U8 → GND; unit B U7 → GND/NC.
- [x] ERC: 0 error; 7 warning (`footprint_link_issues`) — все `excluded`, реальных нарушений нет.
- [x] Отчёты: `session_report_1.4.md`, `session_report_validation.md`; фактический состав зафиксирован в `docs/context.md` и `docs/bom/stage1_control.md`.

---

## 7. Ограничения

- **Плату этапа 1 не травить и не монтировать** до завершения 1.5 + 2.3 и фиксации `docs/contracts/control_pa.md`. — **УЖЕ ВЫПОЛНЕНО (разблокировано):** 1.5 control-часть готова, 2.3 на `02_power_amp` готова, `control_pa.md` зафиксирован (2026-10-28).
- Не менять имена межблочных сигналов (`VFO`, `BFO`, `MODE`, `PTT`, `MIC_LINE`, `MUTE`, `RX_audio`, `+12V_PA`, `+12V_RXTX`, `PWR_LIMIT_EN`, `PWR_LIMIT_SW`) — они зафиксированы в `docs/contracts/`.
- `00_master` не трогать (отложен).
