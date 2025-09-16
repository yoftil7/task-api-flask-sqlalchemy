from marshmallow import (
    Schema,
    fields,
    validate,
    validates,
    pre_load,
    post_dump,
    ValidationError,
    validates_schema,
    EXCLUDE,
)
from .models import User

FORBIDDEN_WORDS = ["shrek", "dummy"]


class TaskSchema(Schema):
    id = fields.Int(dump_only=True)
    description = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=120),
            validate.Regexp(r"^[a-zA-Z0-9 ]+$", error="No special characters allowed"),
        ],
    )
    completed = fields.Bool(required=False, load_default=False)
    priority = fields.Int(required=False, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(dump_only=True)

    # validate against forbidden words
    @validates("description")
    def validate_forbidden_words(self, value, **kwargs):
        lowerd_value = value.lower()
        if any(word in lowerd_value for word in FORBIDDEN_WORDS):
            raise ValidationError(
                f"Task description can not contain: {', '.join(FORBIDDEN_WORDS)}"
            )

    @validates_schema
    def validate_description_content(self, data, **kwargs):
        if data.get("completed") and not data.get("description"):
            raise ValidationError(
                "A Task without description can not be set completed.", "completed"
            )

    # Normalize the data
    @pre_load
    def normalize_description(self, data, **kwargs):
        if "description" in data and isinstance(data["description"], str):
            data["description"] = data["description"].strip().capitalize()
        return data

    # enrich output
    @post_dump
    def enrich_output(self, data, **kwargs):
        data["links"] = {
            "self": f"/tasks/{data['id']}",
            "complete": f"/tasks/{data['id']}/complete",
        }
        return data


class TaskFilterSchema(Schema):
    page = fields.Int(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Int(load_default=10, validate=validate.Range(min=1, max=100))
    completed = fields.Bool(load_default=None)  # optional filter
    sort_by = fields.Str(
        load_default="id",
        validate=validate.OneOf(["id", "priority", "created_at", "description"]),
    )
    sort_order = fields.Str(
        load_default="asc",
        validate=validate.OneOf(["asc", "desc"]),
    )

    class Meta:
        unkown = EXCLUDE


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3))
    password = fields.Str(
        required=True, load_only=True, validate=validate.Length(min=6)
    )  # dont give out password
    role = fields.Str(dump_only=True)

    class Meta:
        unknown = EXCLUDE
