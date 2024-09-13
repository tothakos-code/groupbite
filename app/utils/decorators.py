from functools import wraps
from marshmallow import ValidationError
from flask import request
import logging


def validate_data(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                request_data = schema.load(request.json.get('data', {}))
            except ValidationError as err:
                logging.warning(f"Validation error: {err.messages}")
                return {"error": err.messages}, 400
            return f(request_data, *args, **kwargs)
        return decorated_function
    return decorator
