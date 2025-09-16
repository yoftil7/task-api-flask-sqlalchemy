import pytest
from app import create_app, db
from app.models import Task, User


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


# create a user and get jwt token
@pytest.fixture
def auth_client(client, app):
    with app.app_context():
        user = User(username="testuser")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
    res = client.post(
        "/login", json={"username": "testuser", "password": "password123"}
    )
    token = res.get_json()["access_token"]

    class AuthClient:
        def __init__(self, client, token):
            self.client = client
            self.token = token

        def get(self, url, **kwargs):
            return client.get(
                url, headers={"Authorization": f"Bearer {self.token}"}, **kwargs
            )

        def post(self, url, **kwargs):
            return client.post(
                url, headers={"Authorization": f"Bearer {self.token}"}, **kwargs
            )

        def put(self, url, **kwargs):
            return client.put(
                url, headers={"Authorization": f"Bearer {self.token}"}, **kwargs
            )

        def delete(self, url, **kwargs):
            return client.delete(
                url, headers={"Authorization": f"Bearer {self.token}"}, **kwargs
            )

    return AuthClient(client, token)


# 🌱 Seed helper: add a single task
@pytest.fixture
def add_task(app):
    def _add_task(description="Test Task", completed=False, user_id=1):
        task = Task(description=description, completed=completed, user_id=user_id)
        db.session.add(task)
        db.session.commit()
        return task

    return _add_task


# 🌱 Seed helper: add multiple tasks
@pytest.fixture
def add_tasks(app):
    def _add_tasks(n=5, user_id=1):
        tasks = [Task(description=f"Task {i+1}", user_id=user_id) for i in range(n)]
        db.session.add_all(tasks)
        db.session.commit()
        return tasks

    return _add_tasks
