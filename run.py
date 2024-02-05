#!/bin/env python
from app import create_app
from app import loader
from app.socketio_singleton import SocketioSingleton

app = create_app(debug=True)

if __name__ == '__main__':
    SocketioSingleton.get_instance().run(app,debug=True)
