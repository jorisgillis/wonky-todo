---
name: wonky-todo project overview
description: FastAPI + HTMX + SQLite todo app; single main.py; reviewed twice (2026-04-25 and 2026-04-26 on `improved` branch)
type: project
---

Minimal todo application using FastAPI, HTMX, SQLite (raw sqlite3 module), and Jinja2 templates.
Single Python source file (main.py, ~142 lines). Two Jinja2 templates: index.html and items.html.
Test suite added on `improved` branch: tests/test_main.py (~100 lines).

**Ruff + mypy:** Both pass clean as of 2026-04-26 review.

**Changes made on `improved` branch vs first commit:**
- `get_db()` now correctly uses `@contextmanager` with try/finally; connection isolation is fixed.
- `toggle_completed` now uses a single atomic SQL expression `(completed + 1) % 2`; no race.
- `set_due_date` now correctly attaches UTC timezone before storing ISO string.
- `remove_due_date` and `set_due_date` now return 404 when the id does not exist.
- A DELETE `/todos/{id}` endpoint was added; todos can now be deleted.
- `datetime_local` Jinja2 filter added at module level; template no longer slices in-template.
- `tests/test_main.py` added with coverage of all CRUD operations.

**Remaining issues found on 2026-04-26 review (improved branch):**

- `id` (built-in shadow) used as path parameter name in five route handlers.
- `render_items_html` is a thin one-liner wrapper with no added value; inline it or give it a better name.
- `fetch_all_todos` uses `SELECT *` and returns `list[dict]`; no typed schema.
- `toggle_completed` does not return 404 when the id does not exist (unlike title/due_date).
- `delete_todo` does not return 404 when the id does not exist.
- `index.html` loads htmx from unpkg CDN with no SRI hash (integrity attribute missing or empty).
- No CSRF protection — every mutating route is triggered by HTMX with no token.
- `cursor` variable referenced outside the `with get_db()` block in `update_title` and `set_due_date` and `remove_due_date` — works because sqlite3 cursors are not tied to the connection object in CPython, but it is conceptually unsafe.
- `lifespan` type annotation missing (should be `AsyncGenerator[None, None]`).
- Tests rely on `resp.context` which is a Starlette `TestClient`-specific attribute and is typed as `# type: ignore`; brittle coupling to template context.
- No test for `toggle_completed` returning 200 when id does not exist (silent failure).
- `_create` helper in tests is defined but never used in the test suite.

**Why:** Second-pass review after prototype improvements. Clean lint/mypy is maintained.
**How to apply:** Issues are moderate; the app is still a prototype. Prioritise security (CSRF, SRI) and the silent-failure gaps on delete/toggle.
