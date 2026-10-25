---
alwaysApply: true
---

kicad_create_new_project nests the project into a subfolder named after the project (e.g. KiCad/00_master/00_master/). To avoid this, the agent must account for it: create the project such that files end up in the intended directory. If a project was created in a nested subfolder, FLATTEN it: move all project files (.kicad_pro, .kicad_sch, .kicad_pcb if applicable) up one level into the intended parent directory, then delete the now-empty nested subfolder. Prefer creating projects in the project root so no nesting occurs. File moves/deletes are allowed (they are not S-expression edits); only editing of KiCad file CONTENTS is restricted to MCP tools.