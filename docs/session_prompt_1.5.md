# Промт для KiCad-сессии: подэтап 1.5 (`01_control`) — интерфейсы / GPIO / NC

> Самодостаточный промт. Вставляй целиком в **новый диалог** (контекст сброшен).
> Ты — агент с доступом к KiCad MCP. Работаешь по шагам, ничего не перескакивая.

## 0. Проект и файл

- Активный проект: **`KiCad/01_control`** (`D:\Sources\git-hub\OkunevPY\TRX_27MHz\KiCad\01_control`).
- Целевой файл: **`01_control.kicad_sch`**.
- Перед началом прочитай: `docs/context.md`, `docs/contracts/control_pa.md`, `docs/contracts/control_rxtx.md`, `docs/inter-module-pinout.md`, `docs/bom/stage1_control.md` (раздел 1.5).
- Убедись через `kicad_set_project`, что активен `01_control` (не `00_master`).

> **Контракты:** `control_pa.md` — **ЗАФИКСИРОВАН** (2026-10-28). `control_rxtx.md` — зафиксирован только **пинаут разъёмов** (остальное — черновик до этапа 3). 1.5 выполняется **совместно с 2.3**, после неё разрешается травление платы этапа 1.

## 1. Правила (КРИТИЧНО, не нарушать)

1. `.kicad_sch` / `.kicad_pro` / `.kicad_pcb` править **ТОЛЬКО через KiCad MCP**. `write_file`/`edit_file`/`str_replace` на них запрещены.
2. Не редактировать один файл параллельно. Одна MCP-операция → перечитать → следующая. Не запускать параллельные KiCad-вызовы.
3. **Не запускать `sch_annotate`** — перенумерует зафиксированные refdes.
4. **Никаких наложений** символов/полей/текста/проводов (§6 AGENTS.md). Перед вставкой — `sch_get_bounding_boxes`/`sch_find_free_placement`, после — `sch_visual_qa` (игнорируй ложное «power-на-пине» ~6.5 мм²).
5. Корпуса пассивов: **0603** + **HandSolder**. 10 мкФ → **0805**. (В 1.5 новых пассивов НЕ добавляем — только разводка цепей.)
6. Пины 2-выводных пассивов при rot=0: pin1 сверху = y−3.81 мм, pin2 снизу = y+3.81 мм.
7. Питание и GND — **глобальными метками**. Для «горячих» цепей, где ERC пишет `power_pin_not_driven`, — `power:PWR_FLAG`.
8. Не трогать `sym-lib-table`/`fp-lib-table`.
9. **Имена межблочных сигналов** (источник правды — контракты): `VFO`, `BFO`, `I`, `Q`, `PTT`, `MIC_LINE`, `MUTE`, `RX_audio`, `+12V_PA`, `+12V_RXTX`, `PWR_LIMIT_EN`, `PWR_LIMIT_SW`, `I_sense`, `SWR_sense`. **НЕ менять.**

## 2. Текущее состояние (УЖЕ СДЕЛАНО — НЕ переделывать)

- **1.1–1.4 готовы** (питание, MCU, Si5351+74HC74, U8 74AC541, U9 RT9193 дисплея, разъёмы UI, RC-фильтры, MIC-предусилитель U7, RX_audio RC).
- **ERC baseline: 68 error + 16 warning** — весь остаток «отложено до 1.5» (висящие интерфейсные метки, 28 свободных GPIO MCU, неразведённые разъёмы, изолированные буферные выходы).
- **J_OLED уже разведён** (ST7789 пришёл, сверено, не переделывать): 1=GND, 2=`+3V3_DISP`, 3=`OLED_SCK`, 4=`OLED_MOSI`, 5=`LCD_RST`, 6=`OLED_DC`, 7=`OLED_CS`, 8=`LCD_BLK`. R15–R18 (22 Ом) стоят между MCU-стороной (`SPI_SCK`/`SPI_MOSI`/`SPI_CS`/`SPI_DC` = R15–R18:1) и OLED-стороной (`OLED_*` = R15–R18:2).
- **J_ENC / J_BTN уже разведены** (RC-фильтры на месте): J_ENC 1=GND, 2=+3V3, 3=ENC_SW, 4=ENC_DT, 5=ENC_CLK; J_BTN 1=BTN_UP, 2=BTN_DOWN, 3=BTN_LEFT, 4=BTN_RIGHT, 5=BTN_PUSH, 6=GND, 7=BTN_RIT, 8=GND. Каждая линия уже имеет `R_pu:2` + `C:1` + пин разъёма; **не хватает только MCU-пина**.
- **Буферы U8 74AC541** (входы A3/A4/A7/A8 уже на GND):
  - `VFO_RAW`(U5:10)→U8:2 → `VFO_BUF`(U8:18/R19:1)→**`VFO_OUT`**(R19:2)
  - `BFO_RAW`(U5:9)→U8:3 → `BFO_BUF`(U8:17/R20:1)→**`BFO_OUT`**(R20:2)
  - `I`(U6:12/U6:5/U8:6)→`I_BUF`(U8:14/R21:1)→**`I_OUT`**(R21:2)
  - `Q`(U6:9/U8:7)→`Q_BUF`(U8:13/R22:1)→**`Q_OUT`**(R22:2)
  - `IQ_EN` = U8:19 (GPIO MCU, активный низкий, локально)

**Занятые refdes (не трогать):** C1–C41 (C17 удалён; C22=4.7 мкФ), R1–R28, L1–L3, U1–U9, D1–D3, Y1–Y2, J_OLED / J_ENC / J_BTN / J_PA_CTRL / J_RXTX_SIG / J_PA_PWR / J_RXTX_PWR / J_SWD / J_UART. **В 1.5 новых refdes НЕ добавляем.**

## 3. Цоколёвка MCU U4 (STM32F411CEUx, UFQFPN-48)

Символ `MCU_ST_STM32F4:STM32F411CEUx`. Занятые пины (не трогать): 1(VBAT), 5/6(OSC), 7(NRST), 8(VSSA), 9(VDDA), 22(VCAP), 23/35/47/49(VSS), 24/36/48(VDD), 30(UART_TX), 31(UART_RX), 34(SWDIO), 37(SWDCLK), 42(PB6=I2C_SCL), 43(PB7=I2C_SDA), 44(BOOT0).

Свободные GPIO (номер пина → порт):
2=PC13, 3=PC14, 4=PC15, 10=PA0, 11=PA1, 12=PA2, 13=PA3, 14=PA4, 15=PA5, 16=PA6, 17=PA7, 18=PB0, 19=PB1, 20=PB2, 21=PB10, 25=PB12, 26=PB13, 27=PB14, 28=PB15, 29=PA8, 32=PA11, 33=PA12, 38=PA15, 39=PB3, 40=PB4, 41=PB5, 45=PB8, 46=PB9.

## 4. Назначение GPIO (РЕШЕНО, не менять без согласования)

| Сигнал | Направление | Порт (пин) | Примечание |
|---|---|---|---|
| `I_sense` | IN (ADC) | PA0 (10) | ADC1_IN0 |
| `SWR_sense` | IN (ADC) | PA1 (11) | ADC1_IN1 |
| `RX_audio_F` | IN (ADC) | PA2 (12) | ADC1_IN2 (squelch) |
| `LCD_RST` | OUT | PA3 (13) | GPIO |
| `SPI_CS` | OUT | PA4 (14) | GPIO (software CS) |
| `SPI_SCK` | OUT | PA5 (15) | SPI1_SCK |
| `SPI_DC` | OUT | PA6 (16) | GPIO |
| `SPI_MOSI` | OUT | PA7 (17) | SPI1_MOSI |
| `LCD_BLK` | OUT | PB0 (18) | GPIO / TIM3_CH3 (PWM подсветки, опц.) |
| `BTN_RIGHT` | IN | PB1 (19) | GPIO/EXTI |
| `BTN_PUSH` | IN | PB2 (20) | GPIO/EXTI |
| `PWR_LIMIT_EN` | OUT | PB10 (21) | GPIO |
| `BTN_RIT` | IN | PB12 (25) | GPIO/EXTI |
| `ENC_CLK` | IN | PB13 (26) | GPIO/EXTI |
| `ENC_DT` | IN | PB14 (27) | GPIO/EXTI |
| `ENC_SW` | IN | PB15 (28) | GPIO/EXTI |
| `PTT` | OUT | PA8 (29) | GPIO (один GPIO → 2 разъёма) |
| `PWR_LIMIT_SW` | IN | PA11 (32) | GPIO |
| `MUTE` | OUT | PB8 (45) | GPIO |
| `IQ_EN` | OUT | PB9 (46) | GPIO, активный низкий (→ U8:19) |
| `BTN_UP` | IN | PC13 (2) | GPIO/EXTI |
| `BTN_DOWN` | IN | PC14 (3) | GPIO/EXTI |
| `BTN_LEFT` | IN | PC15 (4) | GPIO/EXTI |

**NC (не используются → `sch_add_no_connect`):** PA12 (33), PA15 (38), PB3 (39), PB4 (40), PB5 (41).

> Все JTAG-пины (PA15/PB3/PB4/PB5) оставлены NC — прошивка работает по SWD (PA13/PA14), JTAG отключать не требуется.

## 5. Коллизия имён I/Q — РЕШЕНИЕ (выполнить ДО разводки)

Сырые выходы 74HC74 **уже называются `I` и `Q`**, а контрактные межплатные пины J_RXTX_SIG:4/5 — тоже `I`/`Q`. Это одна и та же глобальная цепь — ставить её на разъём НЕЛЬЗЯ (закоротит буфер, выход пойдёт в обход U8).

**Переименовать (через `sch_delete_label` + `sch_add_label`/`sch_add_global_label` по тем же координатам):**

| Старое имя | Новое имя | Координаты меток (мм) |
|---|---|---|
| `I` (сырая) | `I_RAW` | (135.89, 246.38), (66.04, 157.48), (46.99, 191.77) |
| `Q` (сырая) | `Q_RAW` | (135.89, 248.92), (69.85, 191.77) |
| `I_OUT` | `I` | (168.91, 160.02) |
| `Q_OUT` | `Q` | (168.91, 181.61) |
| `VFO_OUT` | `VFO` | (168.91, 138.43) |
| `BFO_OUT` | `BFO` | (168.91, 118.11) |

**НЕ трогать** контрактные глобальные метки `I` @ (20.32, 76.2) и `Q` @ (20.32, 83.82) — после переименования они сольются с буферными выходами `I`/`Q`.

После переименования:
- сырые: `VFO_RAW`/`BFO_RAW`/`I_RAW`/`Q_RAW` (вход U8);
- промежуточные: `VFO_BUF`/`BFO_BUF`/`I_BUF`/`Q_BUF` (выход U8 → R_buf);
- **выходы = контрактные имена**: `VFO`/`BFO`/`I`/`Q` (R_buf → J_RXTX_SIG).

## 6. Разводка разъёмов (финальный пинаут из контрактов)

### J_RXTX_SIG (10P, `Connector_JST:JST_XH_B10B-XH-A_1x10_P2.50mm_Vertical`)
1=GND, 2=`VFO`, 3=`BFO`, 4=`I`, 5=`Q`, 6=`RX_audio`, 7=`PTT`, 8=`MIC_LINE`, 9=`MUTE`, 10=GND.

### J_PA_CTRL (6P, `JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical`)
1=GND, 2=`PTT`, 3=`PWR_LIMIT_EN`, 4=`PWR_LIMIT_SW`, 5=`I_sense`, 6=`SWR_sense`.

### J_PA_PWR (клеммник 2P 5.0 мм)
1=`+12V_PA`, 2=GND.

### J_RXTX_PWR (клеммник 2P 5.0 мм)
1=`+12V_RXTX`, 2=GND.

> `PTT` — одна цепь на два разъёма (J_PA_CTRL:2 и J_RXTX_SIG:7), один GPIO PA8.
> `J_RXTX_SIG` имеет **два GND** (пины 1 и 10) — оба на GND.

## 7. Порядок работы (checkpoints)

1. `kicad_set_project` → активен `01_control`; перечитать `docs/context.md`.
2. `sch_get_symbols` → проверить уникальность refdes (не должно быть дублей).
3. **Переименовать** I/Q/VFO/BFO-выходы (§5), перечитывая каждую метку после правки.
4. **Развести разъёмы** J_RXTX_SIG / J_PA_CTRL / J_PA_PWR / J_RXTX_PWR (§6) — по пину.
5. **Назначить GPIO** (§4): поставить глобальную метку сигнала на соответствующий пин U4 (через `sch_get_pin_positions` для U4). Для UI-линий (`BTN_*`/`ENC_*`/`SPI_*`/`LCD_RST`/`LCD_BLK`/`RX_audio_F`) — MCU-пин вливается в уже существующую цепь.
6. **NC** на 5 свободных GPIO (§4) через `sch_add_no_connect`.
7. При `power_pin_not_driven` на `+12V_PA`/`+12V_RXTX` — поставить `power:PWR_FLAG`.
8. `sch_get_symbols` — уникальность refdes; `sch_get_connectivity_graph` — убедиться, что разъёмы/GPIO сведены.
9. `run_erc(save_report=true)` — сравнить с baseline (68 error + 16 warning).
10. Обновить `docs/bom/stage1_control.md` (1.5) и `docs/context.md`.
11. Коммит (`hw:`/`docs:`). **Не коммитить без явного согласия пользователя.**

## 8. Definition of Done

- [ ] Коллизия I/Q устранена (§5): сырые `I_RAW`/`Q_RAW`, выходы `VFO`/`BFO`/`I`/`Q` = контракт.
- [ ] Все 4 разъёма разведены по пинауту §6.
- [ ] Все 23 сигнала заведены на GPIO §4; `PTT` на J_PA_CTRL:2 **и** J_RXTX_SIG:7.
- [ ] 5 свободных GPIO (PA12/PA15/PB3/PB4/PB5) — `no-connect`.
- [ ] Нет коллизий refdes (`sch_get_symbols`).
- [ ] `run_erc(save_report=true)`: нет **новых** `pin_to_pin` / `multiple_net_names` / `power_pin_not_driven` (остаток «Pin not connected» допустим только на NC-пинах).
- [ ] `sch_visual_qa` без новых наложений (кроме ложного «power-на-пине»).
- [ ] Фактическая привязка GPIO зафиксирована в `docs/bom/stage1_control.md` (1.5) и `docs/context.md`.
- [ ] Отчёт: таблица «задача → сделано → отклонения», таблица GPIO, остаточные ERC.

## 9. Что НЕ делать

- Не трогать `00_master`, `sym-lib-table`/`fp-lib-table`.
- Не менять занятую таблицу refdes (§2).
- Не запускать `sch_annotate`.
- Не разводить PCB (`01_control.kicad_pcb`) — только схема.
- Не травить/монтировать плату без завершения **1.5 + 2.3** (2.3 — на стороне PA, отдельная сессия).
- Не добавлять новые компоненты/refdes.
