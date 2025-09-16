from flask import Blueprint, request, jsonify, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .models import db, User
from .schemas import UserSchema

bp = Blueprint("auth", __name__)
user_schema = UserSchema()


@bp.post("/register")
def register():
    data = user_schema.load(request.get_json())
    username = data.get("username")
    password = data.get("password")

    existing_user = db.session.execute(
        db.select(User).filter_by(username=username)
    ).scalar_one_or_none()

    if existing_user:
        abort(400, description=f"Username '{username}' is already taken.")

    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    return jsonify(access_token=access_token, user=user_schema.dump(user)), 201


@bp.post("/login")
def login():
    data = user_schema.load(request.get_json())
    username = data.get("username")
    password = data.get("password")

    user = db.session.execute(
        db.select(User).filter_by(username=username)
    ).scalar_one_or_none()

    if not user or not user.check_password(password):
        abort(401, description="invalid credentials")

    access_token = create_access_token(
        identity=str(user.id), additional_claims={"role": user.role}
    )
    return jsonify(access_token=access_token, user=user_schema.dump(user))


@bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)
    return jsonify(user_schema.dump(user))
