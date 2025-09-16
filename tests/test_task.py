# user authentication related tests


def test_user_registration(client):
    res = client.post("/register", json={"username": "alice", "password": "sercret123"})
    assert res.status_code == 201
    data = res.get_json()
    assert "user" in data
    assert data["user"]["username"] == "alice"
    assert "access_token" in data
    assert isinstance(data["access_token"], str)


def test_user_login(client):
    client.post("/register", json={"username": "alice", "password": "secret123"})
    res = client.post("/login", json={"username": "alice", "password": "secret123"})
    assert res.status_code == 200
    data = res.get_json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)


def test_user_registration_with_duplicate_username(client):
    res1 = client.post("/register", json={"username": "alice", "password": "secret123"})
    assert res1.status_code == 201
    res2 = client.post(
        "/register", json={"username": "alice", "password": "password123"}
    )
    assert res2.status_code == 400
    data2 = res2.get_json()
    assert "error" in data2


def test_user_with_wrong_password(client):
    client.post("/register", json={"username": "alice", "password": "correct_pass"})
    res = client.post("/login", json={"username": "alice", "password": "wrong_pass"})
    assert res.status_code == 401
    data = res.get_json()
    assert "error" in data
    assert data["error"]["type"] == "Unauthorized"


def test_nonexistent_user(client):
    res = client.post(
        "/login", json={"username": "noneexistent_user", "password": "password123"}
    )
    assert res.status_code == 401
    data = res.get_json()
    assert "error" in data
    assert data["error"]["type"] == "Unauthorized"


def test_create_task(auth_client):
    res = auth_client.post("/tasks", json={"description": "New task"})
    assert res.status_code == 201
    data = res.get_json()
    assert data["description"] == "New task"
    assert data["completed"] is False
    assert "id" in data


def test_list_tasks(auth_client, add_tasks):
    add_tasks(3)
    res = auth_client.get("/tasks")
    assert res.status_code == 200
    data = res.get_json()
    assert "items" in data
    assert len(data["items"]) == 3


def test_get_task(auth_client, add_task):
    task = add_task(description="Seeded task")
    res = auth_client.get(f"/tasks/{task.id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["id"] == task.id
    assert data["description"] == "Seeded task"


def test_update_task(auth_client, add_task):
    task = add_task(description="Old Task")
    res = auth_client.put(
        f"/tasks/{task.id}", json={"description": "Updated task", "completed": True}
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["description"] == "Updated task"
    assert data["completed"] is True


def test_delete_task(auth_client, add_task):
    task = add_task(description="Delete Me")
    res = auth_client.delete(f"/tasks/{task.id}")
    assert res.status_code == 204

    # Verify it's gone
    res2 = auth_client.get(f"/tasks/{task.id}")
    assert res2.status_code == 404


# edge cases
def test_create_task_validation_error(auth_client):
    res = auth_client.post("/tasks", json={})  # missing description
    assert res.status_code == 400
    data = res.get_json()
    assert "description" in data["error"]["details"]  # marshmallow error messages


def test_get_task_not_found(auth_client):
    res = auth_client.get("/tasks/40")
    assert res.status_code == 404
    data = res.get_json()
    assert "error" in data


def test_list_tasks_empty(auth_client):
    res = auth_client.get("/tasks")
    assert res.status_code == 200
    data = res.get_json()
    assert data["items"] == []


# pagination test


def test_pagination_first_page(auth_client, add_tasks):
    add_tasks(15)
    res = auth_client.get("/tasks?page=1&per_page=10")
    assert res.status_code == 200
    data = res.get_json()

    assert data["meta"]["page"] == 1
    assert data["meta"]["per_page"] == 10
    assert data["meta"]["total"] == 15
    assert data["meta"]["pages"] == 2
    assert len(data["items"]) == 10
    assert data["meta"]["has_next"] is True
    assert data["meta"]["has_prev"] is False


def test_pagination_second_page(auth_client, add_tasks):
    add_tasks(15)
    res = auth_client.get("/tasks?page=2&per_page=10")
    assert res.status_code == 200
    data = res.get_json()

    assert data["meta"]["page"] == 2
    assert len(data["items"]) == 5
    assert data["meta"]["has_next"] is False
    assert data["meta"]["has_prev"] is True


def test_pagination_invalid_params(auth_client):
    res = auth_client.get("/tasks?page=0&per_page=200")
    assert res.status_code == 400
    data = res.get_json()
    assert "page" in data["error"]["details"]
    assert "per_page" in data["error"]["details"]


def test_http_exception_handler(auth_client):
    # trigger 404
    res = auth_client.get("/none-existing")
    assert res.status_code == 404
    data = res.get_json()
    assert "error" in data
    assert data["error"]["type"] == "NotFound"


def test_generic_exception_handler(app, auth_client, monkeypatch, add_task):
    add_task(description="Test task")

    # Force a crash by monkeypatching the serializer's dump method
    def boom(*args, **kwargs):
        raise RuntimeError("Boom!")

    from app import schemas

    monkeypatch.setattr(schemas.TaskSchema, "dump", boom)

    res = auth_client.get("/tasks/1")
    assert res.status_code == 500
    data = res.get_json()
    assert data["error"]["type"] == "InternalServerError"
