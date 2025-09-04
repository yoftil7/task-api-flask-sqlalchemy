import pytest
from app import create_app, db
from app.models import Task


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


# 🌱 Seed helper: add a single task
@pytest.fixture
def add_task(app):
    def _add_task(description="Test Task", completed=False):
        task = Task(description=description, completed=completed)
        db.session.add(task)
        db.session.commit()
        return task

    return _add_task


# 🌱 Seed helper: add multiple tasks
@pytest.fixture
def add_tasks(app):
    def _add_tasks(n=5):
        tasks = [Task(description=f"Task {i+1}") for i in range(n)]
        db.session.add_all(tasks)
        db.session.commit()
        return tasks

    return _add_tasks
