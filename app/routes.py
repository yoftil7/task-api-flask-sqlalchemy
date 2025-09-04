from flask import Blueprint, request, jsonify, abort
from marshmallow import ValidationError
from .models import Task
from .schemas import TaskSchema, PaginationSchema
from . import db


bp = Blueprint("tasks", __name__)

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
pagination_schema = PaginationSchema()


# health check
@bp.get("/health")
def health():
    return {"status": "ok"}


# create
@bp.post("/tasks")
def create_task():
    json_data = request.get_json(silent=True) or {}
    data = task_schema.load(json_data)

    task = Task(**data)
    db.session.add(task)
    db.session.commit()
    return jsonify(task_schema.dump(task)), 201


# read all
@bp.get("/tasks")
def list_all():
    pagination_params = pagination_schema.load(request.args)

    page = pagination_params["page"]
    per_page = pagination_params["per_page"]
    pagination = db.paginate(
        db.select(Task).order_by(Task.id),
        page=page,
        per_page=per_page,
        error_out=False,  # prevent 404 if page is empty.
    )
    if pagination.page > 1 and not pagination.items:
        abort(404, description="Page not found")

    items = tasks_schema.dump(pagination.items)
    return (
        jsonify(
            {
                "meta": {
                    "page": pagination.page,
                    "per_page": pagination.per_page,
                    "total": pagination.total,
                    "pages": pagination.pages,
                    "has_next": pagination.has_next,
                    "has_prev": pagination.has_prev,
                },
                "items": items,
            }
        ),
        200,
    )


# read one
@bp.get("/tasks/<int:task_id>")
def get_task(task_id: int):
    task_from_db = db.session.get(Task, task_id)
    if not task_from_db:
        abort(404, description="Task not found")
    serialized_task = task_schema.dump(task_from_db)
    return jsonify(serialized_task), 200


# update full or partial
@bp.put("/tasks/<int:task_id>")
def update_task(task_id: int):
    task_from_db = db.session.get(Task, task_id)
    if not task_from_db:
        abort(404, description="Task not found")

    data = task_schema.load(request.get_json(silent=True) or {}, partial=True)
    if "description" in data:
        task_from_db.description = data["description"] or ""
    if "completed" in data:
        task_from_db.completed = bool(data["completed"])

    db.session.commit()
    serialized_task = task_schema.dump(task_from_db)
    return jsonify(serialized_task), 200


# mark complete
@bp.post("/tasks/<int:task_id>/complete")
def mark_complete(task_id: int):
    task_from_db = db.session.get(Task, task_id)
    if not task_from_db:
        abort(404, description="task not found")
    task_from_db.completed = True
    db.session.commit()
    serialized_task = task_schema.dump(task_from_db)
    return jsonify(serialized_task), 200


# delete
@bp.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        abort(404, description="task not found")
    db.session.delete(task)
    db.session.commit()
    return "", 204
