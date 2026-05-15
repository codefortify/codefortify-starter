from django.core.exceptions import ValidationError


def validate_non_empty(value):
    if value is None or not str(value).strip():
        raise ValidationError("This field cannot be empty.")
