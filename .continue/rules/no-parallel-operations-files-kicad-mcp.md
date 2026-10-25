---
alwaysApply: true
---

1) Never edit or create the same file in parallel — apply changes to a single file strictly one operation at a time, re-reading before the next edit if it may have changed. 2) Never issue multiple KiCad MCP requests in parallel — send one KiCad MCP call, wait for the result, then send the next.