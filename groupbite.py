#!/bin/env python
import click
import eventlet
eventlet.monkey_patch(thread=True, time=True)

from app import create_app, create_migration
from app import loader
from app.socketio_singleton import SocketioSingleton


from dotenv import load_dotenv
from pathlib import Path
from os import getenv

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)
APP_HOST = getenv('APP_HOST')
APP_PORT = getenv('APP_PORT')

app = None


@click.group()
def cli():
    """Main entry point for GroupBite."""
    pass

@cli.command("run")
def run():
    """Run the GroupBite application."""
    app = create_app(debug=True)
    SocketioSingleton.get_instance().run(
        app,
        host=APP_HOST,
        port=APP_PORT,
        debug=True
    )

@cli.command("migrate")
def migrate():
    """Generate a new Alembic migration based on model changes."""
    create_migration()
    print(f"Migration generated.")


if __name__ == "__main__":
    cli()
