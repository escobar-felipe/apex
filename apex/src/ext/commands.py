import click
from src.ext.database import db
from src.ext.auth import create_user
from src.models import User
from werkzeug.security import generate_password_hash


def create_db():
    """Creates database"""
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        user = User(username="admin", password=generate_password_hash("admin"), admin=True)
        db.session.add(user)
        db.session.commit()



def drop_db():
    """Cleans database"""
    db.drop_all()


def init_app(app):
    # add multiple commands in a bulk
    for command in [create_db, drop_db]:
        app.cli.add_command(app.cli.command()(command))

    # add a single command
    @app.cli.command()
    @click.option('--username', '-u')
    @click.option('--password', '-p')
    def add_user(username, password):
        """Adds a new user to the database"""
        return create_user(username, password)