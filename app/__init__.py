from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
import logging

db = SQLAlchemy()  # gloabl sql-alchemy instance


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///tasks.db"  # sqllite file in the project root
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(
        app
    )  # bind the app to sqlalchemy(so it knows the config and app content)

    # Import models so SQLAlchemy knows about them
    with app.app_context():
        from .models import Task

        db.create_all()  # if no tables exist create tables

    from .routes import bp as tasks_bp

    # blueprints / routes
    app.register_blueprint(tasks_bp)

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
