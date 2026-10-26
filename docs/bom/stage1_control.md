# BOM — Этап 1: плата управления (01_control)

> Правила: пассивные резисторы/керамика — корпус 0603; footprint — по правилу handsoldering (при наличии), иначе обычный SMD/THT; крупные THT/TO-263/SOT-223 — стандартные (ручная пайка).
>
> **ЭЛЕМЕНТЫ УПРАВЛЕНИЯ (энкодер KY-040, кнопки, OLED-дисплей) монтируются НА КОРПУС и подключаются проводами. На плату ставятся только разъёмы/пады под эти провода — сами элементы управления на плате отсутствуют.**

## Принятые решения по корпусам
- MCU: UFQFPN-48 7x7 (STM32F411CEUx + QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm).
- TVS: SMBJ18A (SMB uni-directional 18В, Device:D_TVS, Diode_SMD:D_SMB_Handsoldering).
- Диод входа: SS34, SMA (Diode_SMD:D_SMA_Handsoldering).
- 74HC74: SOIC-14 (handsolder-варианта в библиотеке нет, используется Package_SO:SOIC-14_3.9x8.7mm_P1.27mm).

## Ключевые позиции (черновик)
| Позиция | Кол-во | Примечание | Альтернатива |
|---------|--------|------------|--------------|
| STM32F411CEU6 | 1 | UFQFPN-48 7x7 | STM32F103C8T6 |
| Si5351A-B-GT | 1 | MSOP-10 | готовый модуль Si5351 |
| 74HC74 | 1 | SOIC-14 | 74HC74 (TSSOP-14) |
| LM2596S-5.0 | 1 | TO-263 | MC34063 + обвязка |
| AMS1117-3.3 | 2 | SOT-223 | RT9193-33 |
| SMBJ18A (TVS) | 1 | Device:D_TVS, D_SMB_Handsoldering | SMBJ15A |
| SS34 | 1 | SMA (D_SMA_Handsoldering) | B340A |
| Кварц 8 МГц | 1 | SJK-6C-8.000-16-30-50-C-50-H (HC-49SM SMD) | — |
| Кварц 27.6 МГц | 1 | TG2520SMN-27.6000M-MCGNNM3 (2520 SMD) | — |
| OLED 0.96" 128×64 I2C синий | 1 | модуль SSD1306, 4-pin I2C, на корпус | — |
| Энкодер KY-040 | 1 | модуль KY-040, на корпус, проводами (на плате — разъём 5-pin) | — |
| Разъёмы | — | SMA, IDC, клеммники, PinHeader под UI | — |

## 1.1 — Входная защита + питание (DC-DC + LDO + +3V3_SI)
| Ref | Позиция | Значение | Кол-во | Символ | Footprint |
|-----|---------|----------|--------|--------|-----------|
| F1 | Предохранитель 3-5 А | — | 1 | Device:Fuse | держатель/SMD |
| D1 | TVS SMBJ18A | SMBJ18A | 1 | Device:D_TVS | Diode_SMD:D_SMB_Handsoldering |
| D2 | Шоттки 40В/3А | SS34 | 1 | Diode:SS34 | Diode_SMD:D_SMA_Handsoldering |
| C1 | Электролит вход | 1000 мкФ/25В | 1 | Device:C_Polarized | CP_Radial_D10.0mm_P5.00mm |
| U1 | DC-DC 5В | LM2596S-5 | 1 | LM2596S-5 | TO-263-3_TabPin2 |
| L1 | Индуктивность | 33 мкГн | 1 | Device:L | THT/крупн. SMD |
| D3 | Диод DC-DC | SS34 | 1 | Diode:SS34 | D_SMA_Handsoldering |
| C3 | Электролит 5В | 470 мкФ/16В | 1 | Device:C_Polarized | CP_Radial_D8.0mm_P3.50mm |
| U2 | LDO 3.3В | AMS1117-3.3 | 1 | AMS1117-3.3 | SOT-223-3_TabPin2 |
| U3 | LDO +3V3_SI | AMS1117-3.3 | 1 | AMS1117-3.3 | SOT-223-3_TabPin2 |
| L2 | Феррит +3V3_SI | FB | 1 | Device:FerriteBead | THT/SMD |
| C_0603 (1.1) | Керамика (100нФ,1мкФ) | — | 6 | Device:C | C_0603_1608Metric_Pad1.08x0.95mm_HandSolder |

## 1.2 — MCU STM32F411 + кварц + SWD + UART
| Ref | Позиция | Значение | Кол-во | Символ | Footprint |
|-----|---------|----------|--------|--------|-----------|
| U4 | MCU STM32F411CEU6 | — | 1 | STM32F411CEUx | QFN-48-1EP_7x7mm_P0.5mm_EP5.6x5.6mm |
| Y1 | Кварц 8 МГц HC-49SM | SJK-6C-8.000-16-30-50-C-50-H | 1 | Device:Crystal | Crystal:Crystal_SMD_HC49-SD_HandSoldering |
| C9,C10 | Нагруз. кварца | 20 пФ | 2 | Device:C | C_0603...HandSolder (NPO) |
| C11–C16 | Развязка VDD | 100 нФ | 6 | Device:C | C_0603...HandSolder |
| C17 | VDDA/VCAP | 1 мкФ | 1 | Device:C | C_0603...HandSolder |
| R1 | BOOT0 pull-down | 10 к | 1 | Device:R | R_0603...HandSolder |
| R2 | NRST pull-up | 10 к | 1 | Device:R | R_0603...HandSolder |
| J_SWD | SWD 4-pin | — | 1 | Conn_01x04 | PinHeader_2.54mm |
| J_UART | UART 4-pin | — | 1 | Conn_01x04 | PinHeader_2.54mm |

## 1.3 — Синтезатор Si5351 + 74HC74 + буферы
| Ref | Позиция | Значение | Кол-во | Символ | Footprint |
|-----|---------|----------|--------|--------|-----------|
| U5 | Si5351A-B-GT | — | 1 | Oscillator:Si5351A-B-GT | Package_SO:MSOP-10_3x3mm_P0.5mm |
| Y2 | Кварц 27.6 МГц TG2520SMN | TG2520SMN-27.6000M-MCGNNM3 | 1 | Device:Crystal | Crystal:Crystal_SMD_2520-4Pin_2.5x2.0mm |
| C18,C19 | Развязка Si5351 | 100 нФ | 2 | Device:C | C_0603...HandSolder |
| U6 | 74HC74 | — | 1 | 74xx:74HC74 (3 юнита: 2 логики + питание) | Package_SO:SOIC-14_3.9x8.7mm_P1.27mm |
| R3,R4 | I2C pull-up | 4.7 к | 2 | Device:R | R_0603...HandSolder |
| BUF | Буферы ВЧ VFO/BFO/IQ | — | — | TBD | 1.5 (VFO_RAW/BFO_RAW пока изолированы) |

## 1.4 — UI / RIT / squelch / MIC-предусилитель
| Ref | Позиция | Значение | Кол-во | Символ | Footprint |
|-----|---------|----------|--------|--------|-----------|
| J_OLED | Разъём под OLED 0.96" I2C | — | 1 | Conn_01x04 | PinHeader_2.54mm (VCC/GND/SCL/SDA) |
| J_ENC | Разъём под KY-040 | — | 1 | Conn_01x05 | PinHeader_2.54mm (CLK/DT/SW/VCC/GND) |
| J_BTN | Разъём под кнопки (корпус) | — | 1 | Conn_01x04 | PinHeader_2.54mm |
| U7 | Предусилитель MIC | op-amp | 1 | TBD | TBD |
| MIC | Цепь bias электрета | 2-10 к + C | — | R,C | 0603 |
| Пады | MIC/PTT/GND | — | — | пады | проводной монтаж |

## 1.5 — Интерфейсы (совместно с 2.3)
| Разъём | Тип | Сигналы |
|--------|-----|---------|
| J_PA_CTRL | IDC-10/2x5 | PTT, I_sense, SWR_sense, PWR_LIMIT_EN/SW, GND |
| J_PA_PWR | клеммник 2-pin 5мм | +12V_PA, GND |
| J_RXTX_SIG | TBD | VFO, BFO, I, Q, RX_audio, PTT, MIC_LINE, MUTE |
| J_RXTX_PWR | клеммник 2-pin | +12V_RXTX, GND |

## Статус
Корпуса зафиксированы (MCU UFQFPN-48, пассивные 0603, handsoldering). 1.1–1.3 схемотехника выполнена; UI (1.4) и интерфейсы (1.5) — в работе. Буферы ВЧ VFO/BFO/IQ уточняются в 1.5.