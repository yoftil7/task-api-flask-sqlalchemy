from marshmallow import (
    Schema,
    fields,
    validate,
    pre_load,
    post_dump,
    ValidationError,
    validates_schema,
)

FORBIDDEN_WORDS = ["test", "dummy"]


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

    # validate against forbidden words
    @validate("description")
    def validate_forbidden_words(self, value):
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
