from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, Task
from .schemas import TaskSchema, TaskFilterSchema
from .utils.decorators import admin_required, role_required
from . import db


bp = Blueprint("tasks", __name__)

task_schema = TaskSchema()
tasks_schema = TaskSchema(many=True)
task_filter_schema = TaskFilterSchema()


# health check
@bp.get("/health")
def health():
    return {"status": "ok"}


# create
@bp.post("/tasks")
@jwt_required()
def create_task():
    data = task_schema.load(request.get_json(silent=True))
    user_id = get_jwt_identity()

    task = Task(user_id=user_id, **data)
    db.session.add(task)
    db.session.commit()
    return jsonify(task_schema.dump(task)), 201


# read all
@bp.get("/tasks")
@jwt_required()
def list_all():
    user_id = get_jwt_identity()
    filters = task_filter_schema.load(request.args)

    page = filters["page"]
    per_page = filters["per_page"]

    query = db.select(Task).filter_by(user_id=user_id)

    # Filtering
    if filters["completed"] is not None:
        query = query.filter(Task.completed == filters["completed"])

    # Sorting
    sort_attr = getattr(Task, filters["sort_by"])
    if filters["sort_order"] == "desc":
        sort_attr = sort_attr.desc()
    query = query.order_by(sort_attr)

    # Pagination
    pagination = db.paginate(
        query,
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
@jwt_required()
def get_task(task_id: int):
    user_id = get_jwt_identity()
    task_from_db = db.session.execute(
        db.select(Task).filter_by(id=task_id, user_id=user_id)
    ).scalar_one_or_none()
    if not task_from_db:
        abort(404, description="Task not found")
    serialized_task = task_schema.dump(task_from_db)
    return jsonify(serialized_task), 200


# update full or partial
@bp.put("/tasks/<int:task_id>")
@jwt_required()
def update_task(task_id: int):
    user_id = get_jwt_identity()
    task_from_db = db.session.execute(
        db.select(Task).filter_by(id=task_id, user_id=user_id)
    ).scalar_one_or_none()
    if not task_from_db:
        abort(404, description="Task not found")

    data = task_schema.load(request.get_json(silent=True) or {}, partial=True)
    if "description" in data:
        task_from_db.description = data["description"]
    if "completed" in data:
        task_from_db.completed = bool(data["completed"])
    if "priority" in data:
        task_from_db.priority = data["priority"]

    db.session.commit()
    serialized_task = task_schema.dump(task_from_db)
    return jsonify(serialized_task), 200


# mark complete
@bp.post("/tasks/<int:task_id>/complete")
@jwt_required()
def mark_complete(task_id: int):
    user_id = get_jwt_identity()
    task_from_db = db.session.execute(
        db.select(Task).filter_by(id=task_id, user_id=user_id)
    ).scalar_one_or_none()
    if not task_from_db:
        abort(404, description="task not found")
    task_from_db.completed = True
    db.session.commit()
    serialized_task = task_schema.dump(task_from_db)
    return jsonify(serialized_task), 200


# delete
@bp.delete("/tasks/<int:task_id>")
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = db.session.execute(
        db.select(Task).filter_by(id=task_id, user_id=user_id)
    ).scalar_one_or_none()
    if not task:
        abort(404, description="task not found")
    db.session.delete(task)
    db.session.commit()
    return "", 204


# special delete route, where by only admin can use.
@bp.delete("/admin/tasks/<int:task_id>")
@admin_required()
@jwt_required()
def delete_all_task(task_id):
    task = db.session.execute(db.select(Task).filter(id=task_id)).scalar_one_or_none()
    if not task:
        abort(404, description="task not found")
    db.session.delete(task)
    db.session.commit()
    return "", 204


@bp.get("/admin/dashboard")
@admin_required()
def admin_dashboard():
    return {"message": "adminstrator dashboard"}


@bp.get("/reports")
@role_required("admin", "manager")
def reports():
    return {"message": "Reports visible for admins & managers"}
