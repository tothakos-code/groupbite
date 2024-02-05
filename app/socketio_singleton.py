from flask_socketio import SocketIO

class SocketioSingleton(object):
    __instance__ = None

    def __init__(self):
        if SocketioSingleton.__instance__ is None:
            SocketioSingleton.__instance__ = SocketIO(logger=True, engineio_logger=True, cors_allowed_origins="*")
        else:
            raise Exception("You cannot create another SocketioSingleton class")

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
        """
        if not SocketioSingleton.__instance__:
            SocketioSingleton()
        return SocketioSingleton.__instance__
