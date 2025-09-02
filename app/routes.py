from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from .models import Task
from .schemas import TaskSchema
from . import db


bp = Blueprint("tasks", __name__)

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)


# health check
@bp.get("/health")
def health():
    return {"status": "ok"}


# create
@bp.post("/tasks")
def create_task():
    try:
        json_data = request.get_json(silent=True) or {}
        data = task_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    task = Task(**data)
    db.session.add(task)
    db.session.commit()
    return jsonify(task_schema.dump(task)), 201


# read all
@bp.get("/tasks")
def list_all():
    tasks_from_db = Task.query.order_by(Task.id).all()
    serialized_tasks = tasks_schema.dump(tasks_from_db)
    return jsonify(serialized_tasks), 200
    # return jsonify([task.to_dict() for task in tasks]), 200


# read one
@bp.get("/tasks/<int:task_id>")
def get_task(task_id: int):
    task_from_db = Task.query.get(task_id)
    if not task_from_db:
        return {"error": "Task not found"}, 404
    serialized_task = task_schema.dump(task_from_db)
    return jsonify(serialized_task), 200


# update full or partial
@bp.put("/tasks/<int:task_id>")
def update_task(task_id: int):
    task_from_db = Task.query.get(task_id)
    if not task_from_db:
        return {"error": "Task not found"}, 404
    try:
        data = task_schema.load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 400
    if "description" in data:
        task_from_db.description = (data["description"] or "").strip()
    if "completed" in data:
        task_from_db.completed = bool(data["completed"])

    db.session.commit()
    serialized_task = task_schema.dump(task_from_db)
    return jsonify(serialized_task), 200


# mark complete
@bp.post("/tasks/<int:task_id>/complete")
def mark_complete(task_id: int):
    task_from_db = Task.query.get(task_id)
    if not task_from_db:
        return {"error": "task not found!"}, 404
    task_from_db.completed = True
    db.session.commit()
    serialized_task = task_schema.dump(task_from_db)
    return jsonify(serialized_task), 200


# delete
@bp.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {"error": "task not found!"}, 404
    db.session.delete(task)
    db.session.commit()
    return "", 204
