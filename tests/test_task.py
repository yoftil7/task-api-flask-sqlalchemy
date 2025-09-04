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
