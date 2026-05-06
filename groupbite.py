#!/bin/env python
import click
import eventlet
eventlet.monkey_patch(thread=True, time=True)

from app import create_app, create_migration, downgrade_migration
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
        debug=False
    )

@cli.command("init")
def init():
    """Generate VAPID keys, Fernet key, and SECRET_KEY; write them to .env."""
    from app.vapid import main as vapid_main
    vapid_main()


@cli.command("migrate")
def migrate():
    """Generate a new Alembic migration based on model changes."""
    create_migration()
    print(f"Migration generated.")


@cli.command("downgrade")
@click.argument("revision", default="-1")
@click.option("--plugin", default=None, help="Plugin name to downgrade (omit for main app).")
def downgrade(revision, plugin):
    """Downgrade the database. REVISION defaults to -1 (one step back), or pass a specific revision ID.
    Use --plugin <name> to downgrade a plugin migration branch instead of the main app."""
    downgrade_migration(revision, plugin=plugin)
    target = f"plugin '{plugin}'" if plugin else "main app"
    print(f"Downgrade {target} to '{revision}' complete.")


if __name__ == "__main__":
    cli()
