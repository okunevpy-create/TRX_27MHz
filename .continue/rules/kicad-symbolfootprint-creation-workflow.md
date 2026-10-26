---
description: "Процедура создания и размещения кастомных символов/footprint'ов
  KiCad: MCP генерирует в output, затем файл переносится в KiCad/libs и
  регистрируется в таблицах библиотек."
alwaysApply: true
---

Кастомные символы (.kicad_sym) и footprint'ы (.kicad_mod) создавать инструментами KiCad MCP (lib_generate_symbol_from_pintable и т.п.), которые пишут в папку output проекта. После генерации файл ПЕРЕНОСИТСЯ (move) в целевую папку KiCad/libs/symbols или KiCad/libs/footprints и регистрируется в sym-lib-table/fp-lib-table. Инструменты MCP не могут писать напрямую в KiCad/libs (ограничение workspace-root), поэтому всегда: генерация в output → перенос в libs → регистрация.