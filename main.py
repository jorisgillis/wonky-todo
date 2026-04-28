import os
import sqlite3
import datetime
from collections.abc import AsyncGenerator, Iterator
from contextlib import asynccontextmanager, contextmanager

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates

DB_PATH: str = os.getenv("DB_PATH", "todos.db")
templates = Jinja2Templates(directory='templates')


def _fmt_datetime_local(dt: str | None) -> str:
    return dt[:16] if dt else ''


templates.env.filters['datetime_local'] = _fmt_datetime_local


@contextmanager
def get_db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    parts = [
        'CREATE TABLE IF NOT EXISTS todos (',
        'id INTEGER PRIMARY KEY AUTOINCREMENT,',
        "title TEXT NOT NULL DEFAULT '',",
        'due_date TEXT,',
        'completed INTEGER NOT NULL DEFAULT 0,',
        'created_at TEXT NOT NULL,',
        'updated_at TEXT NOT NULL)',
    ]
    with get_db() as conn:
        conn.execute(' '.join(parts))
        conn.commit()


def fetch_all_todos() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute('SELECT * FROM todos ORDER BY created_at ASC').fetchall()
    return [dict(r) for r in rows]


def _items_response(request: Request, todos: list[dict]) -> HTMLResponse:
    # Returns only the items fragment; HTMX swaps it into #todo-list without a full page reload.
    return templates.TemplateResponse(request, 'items.html', {'todos': todos})


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get('/', response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, 'index.html', {'todos': fetch_all_todos()})


@app.post('/todos', response_class=HTMLResponse)
async def create_todo(request: Request, title: str = Form('')) -> HTMLResponse:
    t = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with get_db() as conn:
        if title:
            conn.execute(
                'INSERT INTO todos (title,completed,created_at,updated_at) VALUES (?,0,?,?)',
                (title, t, t),
            )
            conn.commit()
    return _items_response(request, fetch_all_todos())


@app.post('/todos/{todo_id}/title', response_class=HTMLResponse)
async def update_title(request: Request, todo_id: int, title: str = Form('')) -> Response:
    if not title:
        return _items_response(request, fetch_all_todos())
    with get_db() as conn:
        cursor = conn.execute(
            'UPDATE todos SET title=?,updated_at=? WHERE id=?',
            (title, datetime.datetime.now(datetime.timezone.utc).isoformat(), todo_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return Response(status_code=404)
    return _items_response(request, fetch_all_todos())


@app.post('/todos/{todo_id}/due_date', response_class=HTMLResponse)
async def set_due_date(request: Request, todo_id: int, due_date: str = Form(...)) -> Response:
    try:
        parsed = datetime.datetime.strptime(due_date, '%Y-%m-%dT%H:%M').replace(
            tzinfo=datetime.timezone.utc
        )
    except ValueError:
        return Response(status_code=422)
    with get_db() as conn:
        cursor = conn.execute(
            'UPDATE todos SET due_date=?,updated_at=? WHERE id=?',
            (parsed.isoformat(), datetime.datetime.now(datetime.timezone.utc).isoformat(), todo_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return Response(status_code=404)
    return _items_response(request, fetch_all_todos())


@app.delete('/todos/{todo_id}/due_date', response_class=HTMLResponse)
async def remove_due_date(request: Request, todo_id: int) -> Response:
    with get_db() as conn:
        cursor = conn.execute(
            'UPDATE todos SET due_date=NULL,updated_at=? WHERE id=?',
            (datetime.datetime.now(datetime.timezone.utc).isoformat(), todo_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return Response(status_code=404)
    return _items_response(request, fetch_all_todos())


@app.post('/todos/{todo_id}/completed', response_class=HTMLResponse)
async def toggle_completed(request: Request, todo_id: int) -> Response:
    with get_db() as conn:
        cursor = conn.execute(
            'UPDATE todos SET completed = ((completed + 1) % 2), updated_at=? WHERE id=?',
            (datetime.datetime.now(datetime.timezone.utc).isoformat(), todo_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return Response(status_code=404)
    return _items_response(request, fetch_all_todos())


@app.delete('/todos/{todo_id}', response_class=HTMLResponse)
async def delete_todo(request: Request, todo_id: int) -> Response:
    with get_db() as conn:
        cursor = conn.execute('DELETE FROM todos WHERE id=?', (todo_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return Response(status_code=404)
    return _items_response(request, fetch_all_todos())
