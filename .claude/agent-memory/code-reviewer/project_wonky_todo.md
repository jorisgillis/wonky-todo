---
name: wonky-todo project overview
description: Small FastAPI + HTMX todo app; single main.py with SQLite backend and Jinja2 templates
type: project
---

Minimal todo application using FastAPI, HTMX, SQLite (raw sqlite3 module), and Jinja2 templates.
Single Python source file (main.py) with one module-level global `_cache` (unused), raw connection
management per request (no connection pooling or context managers), and many naming/style violations.

**Why:** First commit only; likely a learning or prototype project.
**How to apply:** Treat suggestions as greenfield improvements; no existing test suite to protect.
