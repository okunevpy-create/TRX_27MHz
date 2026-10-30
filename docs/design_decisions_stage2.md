# Этап 2 — проектные решения для схемотехники 2.1–2.3

> Фиксируется перед построением схемы `02_power_amp`. Источник правды по составу — `docs/bom/stage2_power_amp.md`; по интерфейсам — `docs/contracts/`.

## 0. Исходные факты (сверено через MCP)
- Схема `02_power_amp` — пустая.
- Символы: `trx_custom:RD16HHF1` (1=GATE, 2=SOURCE, 3=DRAIN); `trx_custom:IM06GR` (8 пинов без имён).
- Символы KiCad: `Device:Transformer_1P_1S` (1=AA, 2=AB, 3=SA, 4=SB), `Device:Transformer_SP_1S` (1=PR1, 2=PM, 3=PR2, 4=S1, 5=S2), `Transistor_FET:2N7002` (1=G, 2=S, 3=D), `Amplifier_Operational:LM358` (1=OUT1, 2=IN1−, 3=IN1+, 4=V−, 5=IN2+, 6=IN2−, 7=OUT2, 8=V+), `Connector:Conn_Coaxial` (1=In, 2=Ext).

## 1. Распиновка реле K1 (IM06GR / 2-1462037-3) — выведено из геометрии символа
Символ `IM00` рисует катушку слева и два перекидных контакта справа. Подвижные (общие) контакты подключены к пинам **3** и **6**; катушка — к **1** (+) и **8** (−).

| Пин | Функция |
|-----|---------|
| 1 | Катушка + |
| 8 | Катушка − |
| 3 | COM1 (подвижный) |
| 2 | NC1 (разрывной) |
| 4 | NO1 (замыкающий) |
| 6 | COM2 (подвижный) |
| 7 | NC2 (разрывной) |
| 5 | NO2 (замыкающий) |

Используется полюс 1: COM1→`ANT`, NO1→`LPF_OUT`(TX), NC1→`RX_RF`. Полюс 2 (5/6/7) — не подключён (резерв).

## 2. Смещение затворов (2.3)
- Делитель: `+12V_PA → R_vgg_top(10k) → VGG_FULL → R_vgg_bot(2.7k) → GND` → ≈2.5 В.
- RV1 (3296W 10k) между `VGG_FULL` и GND, движок = `VGG_LIMIT`.
- `J_SW_1`: 1=`VGG`, 2=`VGG_LIMIT`, 3=`VGG_FULL`, 4=`PWR_LIMIT_SW`, 5=`PLIM_LIM`, 6=`GND`.
- Подача на затворы: `VGG → R_gb1/R_gb2 (10k) → Q1/Q2.GATE`. R_g (4.7 Ом) — антипаразитные последовательно с балуном.
- `C_vgg` (100 нФ) — развязка узла VGG.
- Значения «по расчёту», финально на плате по току покоя.

## 3. LIMIT/FULL + PWR_LIMIT (2.3)
- Полюс B: `+12V_PA → R_lim_pu(27k) → PLIM_LIM → R_lim_pd(10k) → GND` = 3.24 В. `PLIM_LIM→J_SW_1:5`, `J_SW_1:4→PWR_LIMIT_SW→J_PA_CTRL_1:4`, `J_SW_1:6→GND`.
- `PWR_LIMIT_EN` (J_PA_CTRL_1:3) → Q_lim(2N7002) gate; Q_lim D→`VGG`, S→`VGG_LIMIT` (принудительно подключает подстроечник).

## 4. LED «LIMIT активен» = (тумблер LIMIT) ИЛИ (PWR_LIMIT_EN)
- Диодное ИЛИ: D_or1 (A←`PWR_LIMIT_SW`), D_or2 (A←`PWR_LIMIT_EN`), катоды → `LIMIT_ACTIVE`.
- `LIMIT_ACTIVE → R_led_b → D_lim_b → GND` (платный дубль) и `LIMIT_ACTIVE → R_led → J_LIM_LED_1:1` (панель).
- **Добавка к BOM:** D_or1/D_or2 = 1N4148WS ×2 (аналог D_rel). Пометить в BOM.

## 5. I_sense (2.3) — низкосторонний шунт
- R_shunt (0.05 Ом) в минусовой шине: `GND_PA → R_shunt → GND`.
- LM358 канал A неинвертирующий: IN1+ ← `GND_PA`; IN1− ← R_sen_in(1k)→GND и R_sen_fb(22k)→OUT1; G≈23 (≈3.3 В на 2.9 А). OUT1 → R_sen_out(1k) → `I_sense` → J_PA_CTRL_1:5; C_sen(100нФ) фильтр.
- Канал B неиспользуем: IN2+ → GND, IN2− → OUT2 (повторитель).

## 6. SWR_sense (2.3) — упрощённый детектор
- T_swr (BN-61-202, `Device:L`): 1→GND, 2→`SWR_RF` (вторичка; первичка = 1 проход линии ANT физически).
- D_swr1(BAT54): A←`SWR_RF`, K→`SWR_DC` (выпрямитель); D_swr2: A→GND, K→`SWR_RF` (фиксатор). C_swr(100нФ)+R_swr(10k) фильтр/нагрузка. `SWR_DC → SWR_sense → J_PA_CTRL_1:6`.
- Полный мост Стоктона — на доработку (место зарезервировано).

## 7. J_ANT_1 (плата)
- BNC BJ2 — на задней крышке (панель), коаксиалом на плату. На плате — SMA edge-mount (s-p215, как J_RF_TX_1/J_RF_RX_1) как точка подключения коаксиала: `Connector_Coaxial:SMA_Amphenol_132289_EdgeMount`.

## 8. Драйвер-каскад
- Не ставим (расчёт: запас ×1.67 / +2.2 дБ). R_fb1/R_fb2 (150 Ом) — резервное место под ОС, помечены DNP.

## 9. Добавки к BOM (подтвердить)
- R_gb1/R_gb2 (10k), R_vgg_top (10k), R_vgg_bot (2.7k), C_vgg (100нФ), R_sen_in (1k), R_sen_fb (22k), R_sen_out (1k), C_sen (100нФ), R_swr (10k), C_swr (100нФ) — резисторы/керамика 0603 (склад).
- D_or1/D_or2 (1N4148WS ×2) — дозаказ.
