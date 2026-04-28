import re
import pytest
from fastapi.testclient import TestClient


def _todo_ids(html: str) -> list[int]:
    return [int(m) for m in re.findall(r'hx-post="/todos/(\d+)/completed"', html)]


@pytest.fixture
def client(monkeypatch, tmp_path):
    import main
    monkeypatch.setattr(main, "DB_PATH", str(tmp_path / "test.db"))
    main.init_db()
    with TestClient(main.app) as c:
        yield c


def test_index_empty(client: TestClient) -> None:
    resp = client.get("/")
    assert resp.status_code == 200


def test_create_todo(client: TestClient) -> None:
    resp = client.post("/todos", data={"title": "buy milk"})
    assert resp.status_code == 200
    assert "buy milk" in resp.text


def test_create_todo_empty_title_no_error(client: TestClient) -> None:
    resp = client.post("/todos", data={"title": ""})
    assert resp.status_code == 200


def test_update_title(client: TestClient) -> None:
    resp = client.post("/todos", data={"title": "old title"})
    todo_id = _todo_ids(resp.text)[0]
    resp = client.post(f"/todos/{todo_id}/title", data={"title": "new title"})
    assert resp.status_code == 200
    assert "new title" in resp.text


def test_update_title_unknown_id(client: TestClient) -> None:
    resp = client.post("/todos/9999/title", data={"title": "x"})
    assert resp.status_code == 404


def test_toggle_completed(client: TestClient) -> None:
    resp = client.post("/todos", data={"title": "finish tests"})
    todo_id = _todo_ids(resp.text)[0]
    assert "checked" not in resp.text

    resp = client.post(f"/todos/{todo_id}/completed")
    assert "checked" in resp.text

    resp = client.post(f"/todos/{todo_id}/completed")
    assert "checked" not in resp.text


def test_toggle_completed_unknown_id(client: TestClient) -> None:
    resp = client.post("/todos/9999/completed")
    assert resp.status_code == 404


def test_set_due_date(client: TestClient) -> None:
    resp = client.post("/todos", data={"title": "task"})
    todo_id = _todo_ids(resp.text)[0]
    resp = client.post(f"/todos/{todo_id}/due_date", data={"due_date": "2025-12-31T09:00"})
    assert resp.status_code == 200
    assert "2025-12-31T09:00" in resp.text


def test_set_due_date_invalid(client: TestClient) -> None:
    resp = client.post("/todos", data={"title": "task"})
    todo_id = _todo_ids(resp.text)[0]
    resp = client.post(f"/todos/{todo_id}/due_date", data={"due_date": "not-a-date"})
    assert resp.status_code == 422


def test_remove_due_date(client: TestClient) -> None:
    resp = client.post("/todos", data={"title": "task"})
    todo_id = _todo_ids(resp.text)[0]
    client.post(f"/todos/{todo_id}/due_date", data={"due_date": "2025-12-31T09:00"})
    resp = client.delete(f"/todos/{todo_id}/due_date")
    assert resp.status_code == 200
    assert "2025-12-31T09:00" not in resp.text


def test_delete_todo(client: TestClient) -> None:
    resp = client.post("/todos", data={"title": "to delete"})
    todo_id = _todo_ids(resp.text)[0]
    resp = client.delete(f"/todos/{todo_id}")
    assert resp.status_code == 200
    assert "to delete" not in resp.text


def test_delete_todo_unknown_id(client: TestClient) -> None:
    resp = client.delete("/todos/9999")
    assert resp.status_code == 404
