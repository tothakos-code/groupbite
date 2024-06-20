from datetime import date, timedelta, datetime
from app.entities import Session
from app.entities.user import User

class UserService:
    """docstring for UserService."""
    # We need to make sure that username are unique.
    def username_to_id(username):
        session = Session()
        user = session.query(User).filter(User.username == username).first()

        if not user:
            return None
        return user.id


    def id_to_username(id):
        session = Session()
        user = session.query(User).filter(User.id == id).first()

        if not user:
            return None
        return user.username

    def get_user_by_id(id):
        session = Session()
        user = session.query(User).filter(User.id == id).first()

        if not user:
            return None
        return user

    def user_exist(id):
        session = Session()
        user = session.query(User).filter(User.id == id).first()

        if not user:
            return False
        return True

    def username_exist(username):
        session = Session()
        user = session.query(User).filter(User.username == username).first()

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
            return False, "Ez nem lehet a neved: " + username

        notvalid_characters = ["'", '"', "=", ",", ".", "&", "@", "#", "<", ">", "(", ")","[", "]", "{", "}"]
        for char in notvalid_characters:
            if char in username:
                return False, "Tiltott karakter a felhasználónévben: " + char

        if UserService.username_exist(username):
            return False, "Ez a felhasználónév már foglalt"

        return True, ""
