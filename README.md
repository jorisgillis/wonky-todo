# wonky-todo

A deliberately broken Python to-do list application.

> **This project is NOT an example of good Python development.**
> It exists solely as a target corpus for testing a code review agent.
> The code intentionally violates style guides and best practices.
> Do not use it as a reference for how to write Python.

An improvement of the code is included in the branch `improved`. The
code in that branch was obtained by running the [`code-reviewer`
agent](https://github.com/jorisgillis/claude-agents).

---

## Purpose

This repo is a sandbox for evaluating an automated code review agent — specifically one powered by [Ruff](https://docs.astral.sh/ruff/) and [Mypy](https://mypy.readthedocs.io/). The goal is to give the agent a realistic but deliberately flawed codebase and measure how many issues it can detect and explain.

The code breaks as many [PEP 8](https://peps.python.org/pep-0008/) rules as possible on purpose. If you open `main.py` and cringe, that is working as intended.

---

## The Application

A minimal to-do list web app. One page, no JavaScript frameworks, no ORM.

**Stack:**
- Python 3.13
- [FastAPI](https://fastapi.tiangolo.com/) — HTTP layer
- [Jinja2](https://jinja.palletsprojects.com/) — server-side HTML templates
- [HTMX](https://htmx.org/) — in-page interactivity without a full page reload
- SQLite — persistence via raw SQL (no ORM)

**Features:**
- View all to-do items on a single page
- Create a new item by typing in the empty row at the bottom and pressing Enter
- Edit a title inline — changes are persisted automatically when focus leaves the field
- Set an optional due date via a datetime picker — saved immediately on selection
- Remove a due date with the x button
- Toggle an item complete/incomplete
- Delete an item
- `created_at` / `updated_at` audit timestamps on every row

---

## Running locally

```bash
uv run uvicorn main:app --reload
```

Then open `http://localhost:8000`.

---

## Why the code looks the way it does

Every rule in PEP 8 is a target, not a guideline. Naming conventions, line length, import order, whitespace, use of functional constructs where imperative ones are clearer — all of it is intentionally wrong. The only constraint was that the app had to actually run.

**Do not submit pull requests to "fix" the style. The messiness is the point.**

---

## Running the linters (what the review agent does)

```bash
uv run ruff check .
uv run mypy main.py
```

The volume of output these produce is what the agent is evaluated against.
