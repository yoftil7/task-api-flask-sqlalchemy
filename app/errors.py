from flask import jsonify, current_app
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException
import sys, logging


def handle_validation_error(err):
    current_app.logger.warning("Validation failed %s", err.messages)
    return (
        jsonify(
            {
                "error": {
                    "code": 400,
                    "message": "validation failed",
                    "type": "ValidationError",
                    "details": err.messages,
                }
            }
        ),
        400,
    )


def handle_http_exception(err):
    code = err.code
    name = err.name
    if 400 <= code < 500:
        current_app.logger.warning("Client side error (%s): %s", code, message)
    elif code >= 500:
        current_app.logger.error("Server side error (%s): %s", code, message)

    message = (
        err.description if hasattr(err, "description") and err.description else name
    )
    return (
        jsonify(
            {"error": {"code": code, "message": message, "type": name.replace(" ", "")}}
        ),
        code,
    )


def handle_generic_exception(err):
    current_app.logger.exception("Unhandled exception: %s", err)  # includes traceback
    return (
        jsonify(
            {
                "error": {
                    "code": 500,
                    "message": "An un expected error occurred",
                    "type": "InternalServerError",
                }
            }
        ),
        500,
    )
