---
description: При выборе посадочных мест в KiCad отдавать предпочтение вариантам
  для ручной пайки (HandSolder / handsoldering), когда они доступны в
  библиотеке.
alwaysApply: true
---

При выборе footprint для компонента в первую очередь использовать вариант для ручной пайки (в библиотеках KiCad это суффикс/имя с HandSolder или handsoldering, например Package_SO:SOIC-8_3.9x4.9mm_P1.27mm_HandSolder, Package_TO_SOT_SMD:SOT-23_Handsoldering и т.п.). Только если handsoldering-варианта нет, использовать обычный SMD/THT footprint. Для THT-компонентов и разъёмов — стандартные посадочные места под ручной монтаж. Решение о footprint фиксировать в BOM и заметках этапа.