#!/bin/env python
from app import create_app
from app import loader
from app.socketio_singleton import SocketioSingleton


from dotenv import load_dotenv
from pathlib import Path
from os import getenv

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
APP_HOST = getenv('APP_HOST')
APP_PORT = getenv('APP_PORT')

app = create_app(debug=True)

if __name__ == '__main__':
    SocketioSingleton.get_instance().run(
        app,
        host=APP_HOST,
        port=APP_PORT,
        debug=True
    )
