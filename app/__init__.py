from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
import logging
import os


db = SQLAlchemy()  # gloabl sql-alchemy instance


def create_app():
    app = Flask(__name__)

    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, "..", "instance", "tasks.db")
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = (
        "super-secret-key"  # i will change this in production
    )

    db.init_app(
        app
    )  # bind the app to sqlalchemy(so it knows the config and app content)
    JWTManager(app)

    from .routes import bp as tasks_bp
    from .auth_routes import bp as auth_bp

    # blueprints / routes
    app.register_blueprint(tasks_bp)
    app.register_blueprint(auth_bp)

    # logging basic info
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    from .errors import (
        handle_generic_exception,
        handle_http_exception,
        handle_validation_error,
    )

    # Global error handlers
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(HTTPException, handle_http_exception)
    app.register_error_handler(Exception, handle_generic_exception)

    return app
