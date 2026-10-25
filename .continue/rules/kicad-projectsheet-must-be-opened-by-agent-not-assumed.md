---
alwaysApply: true
---

Before ANY KiCad operation (schematic or PCB), the agent MUST itself ensure the correct project and file are open — never assume the user has opened it. Procedure: (1) Check the project file exists (e.g. `.kicad_pro`, the `.kicad_sch`/`.kicad_pcb`). (1.1) If it does not exist, create it. (2) Open/set the project and target file explicitly via KiCad MCP (e.g. `kicad_set_project` with project_dir + sch_file/pcb_file). Only after confirming the active project/file matches the intended one may the agent proceed with edits. This applies to any KiCad object — schematic or PCB.