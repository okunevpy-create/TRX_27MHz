---
alwaysApply: true
---

# KiCad Project and Agent Rules

## 1. Project Creation & Flattening
`kicad_create_new_project` nests the project into a subfolder named after the project (e.g. KiCad/00_master/00_master/). To avoid this, the agent must account for it: create the project such that files end up in the intended directory. If a project was created in a nested subfolder, FLATTEN it: move all project files (`.kicad_pro`, `.kicad_sch`, `.kicad_pcb` if applicable) up one level into the intended parent directory, then delete the now-empty nested subfolder. Prefer creating projects in the project root so no nesting occurs. File moves/deletes are allowed (they are not S-expression edits); only editing of KiCad file CONTENTS is restricted to MCP tools.

## 2. Project State Verification
Before ANY KiCad operation (schematic or PCB), the agent MUST itself ensure the correct project and file are open — never assume the user has opened it. 

Procedure:
1. Check the project file exists (e.g. `.kicad_pro`, the `.kicad_sch`/`.kicad_pcb`).
   * If it does not exist, create it.
2. Open/set the project and target file explicitly via KiCad MCP (e.g. `kicad_set_project` with project_dir + sch_file/pcb_file).

Only after confirming the active project/file matches the intended one may the agent proceed with edits. This applies to any KiCad object — schematic or PCB.

## 3. Concurrency Restrictions
1. Never edit or create the same file in parallel — apply changes to a single file strictly one operation at a time, re-reading before the next edit if it may have changed.

