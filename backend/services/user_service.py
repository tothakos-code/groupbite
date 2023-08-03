from entities.user import User, UserSchema, subscribe_type, daily_state_type
from datetime import date, timedelta, datetime
from entities.entity import Session

class UserService:
    """docstring for UserService."""
    # We need to make sure that username are unique.
    def username_to_id(username):
        session = Session()
        user = session.query(User).filter(User.username == username).first()
        session.close()
        if not user:
            return None
        return user.id


    def id_to_username(id):
        session = Session()
        user = session.query(User).filter(User.id == id).first()
        session.close()
        if not user:
            return None
        return user.username

    def user_exist(id):
        session = Session()
        user = session.query(User).filter(User.id == id).first()
        session.close()
        if not user:
            return False
        return True

    def username_exist(username):
        session = Session()
        user = session.query(User).filter(User.username == username).first()
        session.close()
        if not user:
            return False
        return True


    def is_username_valid(username):
        notvalid_usernames = [
            "null",
            "None",
            None,
            "undefined",
            ""
        ]
        if username in notvalid_usernames:
            return False

        notvalid_characters = ["'", '"', "=", ",", ".", "&", "@", "#", "<", ">", "(", ")","[", "]", "{", "}"]
        for char in notvalid_characters:
            if char in username:
                return False

        if UserService.username_exist(username):
            return False

        return True
