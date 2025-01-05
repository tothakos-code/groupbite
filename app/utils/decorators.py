from functools import wraps
from marshmallow import ValidationError
from flask import request, session
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

def validate_url_params(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                schema.load(kwargs)
            except ValidationError as err:
                logging.warning(f"Validation error: {err.messages}")
                return {"error": err.messages}, 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logging.warning("User not authenticated")
            return { "error": "Unauthorized" }, 401
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.entities.user import User
        if not User.is_admin(session['user_id']):
            logging.warning("User unauthorized")
            return { "error": "Unauthorized" }, 401
        return f(*args, **kwargs)
    return decorated_function
