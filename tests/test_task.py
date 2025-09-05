def test_create_task(client):
    res = client.post("/tasks", json={"description": "New task"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["description"] == "New task"
    assert data["completed"] is False
    assert "id" in data


def test_list_tasks(client, add_tasks):
    add_tasks(3)
    res = client.get("/tasks")
    assert res.status_code == 200
    data = res.get_json()
    assert "items" in data
    assert len(data["items"]) == 3


def test_get_task(client, add_task):
    task = add_task(description="Seeded task")
    res = client.get(f"/tasks/{task.id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == task.id
    assert data["description"] == "Seeded task"


def test_update_task(client, add_task):
    task = add_task(description="Old Task")
    res = client.put(
        f"/tasks/{task.id}", json={"description": "Updated task", "completed": True}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["description"] == "Updated task"
    assert data["completed"] is True


def test_delete_task(client, add_task):
    task = add_task(description="Delete Me")
    res = client.delete(f"/tasks/{task.id}")
    assert res.status_code == 204

    # Verify it's gone
    res2 = client.get(f"/tasks/{task.id}")
    assert res2.status_code == 404


# edge cases
def test_create_task_validation_error(client):
    res = client.post("/tasks", json={})  # missing description
    assert res.status_code == 400
    data = res.get_json()
    assert "description" in data["error"]["details"]  # marshmallow error messages


def test_get_task_not_found(client):
    res = client.get("/tasks/40")
    assert res.status_code == 404
    data = res.get_json()
    assert "error" in data


def test_list_tasks_empty(client):
    res = client.get("/tasks")
    assert res.status_code == 200
    data = res.get_json()
    assert data["items"] == []


# pagination test


def test_pagiantion_first_page(client, add_tasks):
    add_tasks(15)
    res = client.get("/tasks?page=1&per_page=10")
    assert res.status_code == 200
    data = res.get_json()

    assert data["meta"]["page"] == 1
    assert data["meta"]["per_page"] == 10
    assert data["meta"]["total"] == 15
    assert data["meta"]["pages"] == 2
    assert len(data["items"]) == 10
    assert data["meta"]["has_next"] is True
    assert data["meta"]["has_prev"] is False


def test_pagination_second_page(client, add_tasks):
    add_tasks(15)
    res = client.get("/tasks?page=2&per_page=10")
    assert res.status_code == 200
    data = res.get_json()

    assert data["meta"]["page"] == 2
    assert len(data["items"]) == 5
    assert data["meta"]["has_next"] is False
    assert data["meta"]["has_prev"] is True


def test_pagination_invalid_params(client):
    res = client.get("/tasks?page=0&per_page=200")
    assert res.status_code == 400
    data = res.get_json()
    assert "page" in data["error"]["details"]
    assert "per_page" in data["error"]["details"]


def test_http_exception_handler(client):
    # trigger 404
    res = client.get("/none-existing")
    assert res.status_code == 404
    data = res.get_json()
    assert "error" in data
    assert data["error"]["type"] == "NotFound"


def test_generic_exception_handler(app, client, monkeypatch, add_task):
    add_task(description="Test task")

    # Force a crash by monkeypatching the serializer's dump method
    def boom(*args, **kwargs):
        raise RuntimeError("Boom!")

    from app import schemas

    monkeypatch.setattr(schemas.TaskSchema, "dump", boom)

    res = client.get("/tasks/1")
    assert res.status_code == 500
    data = res.get_json()
    assert data["error"]["type"] == "InternalServerError"
