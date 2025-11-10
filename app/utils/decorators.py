from functools import wraps
from marshmallow import ValidationError
from flask import request, session
from app.db.session import get_session_context
import logging

from app.repositories.user_repository import UserRepository


def validate_data(schema):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                request_data = schema.load(request.json.get('data', {}))
            except ValidationError as err:
                logging.warning(f"Validation error: {err.messages}")
                return {"error": err.messages}, 400
            return f(data=request_data, *args, **kwargs)
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
        with get_session_context() as db:
            if not UserRepository(db).is_admin(session['user_id']):
                logging.warning("User unauthorized")
                return { "error": "Unauthorized" }, 401
        return f(*args, **kwargs)
    return decorated_function

def handle_request(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        # this creates the request scoped database session
        with get_session_context() as db:
            try:
                return f(self, db=db, *args, **kwargs)
            except ValueError as e:
                logging.warning(f"Bad request in {f.__name__}: {e}")
                return {"error": str(e)}, 400
            except Exception as e:
                logging.exception(f"Internal server error in {f.__name__}: {e}")
                return {"error": "Internal server error"}, 500
    return wrapper