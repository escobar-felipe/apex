import click
import shutil
import secrets
import sqlite3
import subprocess
from pathlib import Path
from src.ext.database import db
from src.ext.auth import create_user, get_or_create_tenant
from src.models import Tenant, User
from src.config import get_settings
from src.utils.security import encrypt_secret, is_encrypted_secret
from werkzeug.security import generate_password_hash
from sqlalchemy import inspect, text
from sqlalchemy.engine import make_url


def ensure_tenant_columns():
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()

    if "user" in table_names:
        user_columns = {column["name"] for column in inspector.get_columns("user")}
        if "tenant_id" not in user_columns:
            db.session.execute(text('ALTER TABLE "user" ADD COLUMN tenant_id INTEGER'))

    if "searchresults" in table_names:
        result_columns = {column["name"] for column in inspector.get_columns("searchresults")}
        if "tenant_id" not in result_columns:
            db.session.execute(text('ALTER TABLE searchresults ADD COLUMN tenant_id INTEGER'))

    db.session.commit()


def create_db():
    """Creates database"""
    db.create_all()
    ensure_tenant_columns()
    settings = get_settings()
    tenant = get_or_create_tenant(slug=settings.default_tenant_slug, name="Default")
    db.session.execute(text('UPDATE "user" SET tenant_id = :tenant_id WHERE tenant_id IS NULL'), {"tenant_id": tenant.id})
    db.session.execute(text('UPDATE searchresults SET tenant_id = :tenant_id WHERE tenant_id IS NULL'), {"tenant_id": tenant.id})
    db.session.commit()
    if settings.bootstrap_admin_username and settings.bootstrap_admin_password and not User.query.filter_by(username=settings.bootstrap_admin_username, tenant_id=tenant.id).first():
        user = User(username=settings.bootstrap_admin_username, password=generate_password_hash(settings.bootstrap_admin_password), admin=True, tenant_id=tenant.id)
        db.session.add(user)
        db.session.commit()



def drop_db():
    """Cleans database"""
    db.drop_all()


def _database_url():
    return make_url(db.engine.url.render_as_string(hide_password=False))


def _sqlite_database_path(url):
    if url.drivername != "sqlite":
        return None
    if url.database in {None, "", ":memory:"}:
        return None
    return url.database


def backup_db(output):
    """Creates a database backup."""
    url = _database_url()
    sqlite_path = _sqlite_database_path(url)

    if sqlite_path:
        destination = output or f"{sqlite_path}.backup"
        source = sqlite3.connect(sqlite_path)
        try:
            target = sqlite3.connect(destination)
            try:
                source.backup(target)
            finally:
                target.close()
        finally:
            source.close()
        click.echo(f"SQLite backup created at {destination}")
        return

    if not url.drivername.startswith("postgresql"):
        raise RuntimeError(f"Backup is not configured for database driver: {url.drivername}")

    destination = output or "apex-backup.dump"
    if not shutil.which("pg_dump"):
        raise RuntimeError("pg_dump was not found. Install PostgreSQL client tools to run backups.")
    subprocess.run(["pg_dump", "--format=custom", "--file", destination, str(url)], check=True)
    click.echo(f"PostgreSQL backup created at {destination}")


def restore_db(input_path):
    """Restores a database backup."""
    url = _database_url()
    sqlite_path = _sqlite_database_path(url)

    if not input_path:
        raise RuntimeError("Provide --input with the backup path.")
    if not Path(input_path).is_file():
        raise RuntimeError(f"Backup file not found: {input_path}")

    if sqlite_path:
        source = sqlite3.connect(input_path)
        try:
            target = sqlite3.connect(sqlite_path)
            try:
                source.backup(target)
            finally:
                target.close()
        finally:
            source.close()
        click.echo(f"SQLite backup restored into {sqlite_path}")
        return

    if not url.drivername.startswith("postgresql"):
        raise RuntimeError(f"Restore is not configured for database driver: {url.drivername}")
    if not shutil.which("pg_restore"):
        raise RuntimeError("pg_restore was not found. Install PostgreSQL client tools to restore backups.")
    subprocess.run(["pg_restore", "--clean", "--if-exists", "--no-owner", "--dbname", str(url), input_path], check=True)
    click.echo("PostgreSQL backup restored")


def encrypt_existing_credentials():
    users = User.query.all()
    changed = 0

    for user in users:
        for field_name in ["_api_key", "_serpapi_key", "_stmp_password"]:
            raw_value = getattr(user, field_name)
            if raw_value and not is_encrypted_secret(raw_value):
                setattr(user, field_name, encrypt_secret(raw_value))
                changed += 1

    db.session.commit()
    return changed


def init_app(app):
    # add multiple commands in a bulk
    for command in [create_db, drop_db]:
        app.cli.add_command(app.cli.command()(command))

    @app.cli.command()
    @click.option('--output', '-o', default=None)
    def backup_database(output):
        """Creates a database backup."""
        backup_db(output)

    @app.cli.command()
    @click.option('--input', 'input_path', '-i', required=True)
    def restore_database(input_path):
        """Restores a database backup."""
        restore_db(input_path)

    @app.cli.command()
    def encrypt_credentials():
        """Encrypts existing plaintext user credentials."""
        changed = encrypt_existing_credentials()
        click.echo(f"Encrypted credential fields: {changed}")

    # add a single command
    @app.cli.command()
    @click.option('--username', '-u')
    @click.option('--password', '-p')
    @click.option('--tenant', '-t', default=None)
    @click.option('--admin/--no-admin', default=False)
    def add_user(username, password, tenant, admin):
        """Adds a new user to the database"""
        user = create_user(username, password, tenant_slug=tenant)
        if admin:
            user.admin = True
            db.session.commit()
        return user

    @app.cli.command()
    @click.option('--username', '-u', required=True)
    @click.option('--password', '-p', required=True)
    @click.option('--tenant', '-t', default=None)
    def set_user_password(username, password, tenant):
        """Updates an existing user's password"""
        settings = get_settings()
        tenant_slug = tenant or settings.default_tenant_slug
        tenant_model = get_or_create_tenant(slug=tenant_slug)
        user = User.query.filter_by(username=username, tenant_id=tenant_model.id).first()
        if not user:
            raise RuntimeError(f'{username} nao encontrado no tenant {tenant_model.slug}')
        user.password = generate_password_hash(password)
        db.session.commit()
        click.echo(f"Password updated for {username} on tenant {tenant_model.slug}")

    @app.cli.command()
    @click.option('--username', '-u', default='admin')
    @click.option('--tenant', '-t', default=None)
    def disable_default_password(username, tenant):
        """Replaces a known default password with a random value"""
        settings = get_settings()
        tenant_slug = tenant or settings.default_tenant_slug
        tenant_model = get_or_create_tenant(slug=tenant_slug)
        user = User.query.filter_by(username=username, tenant_id=tenant_model.id).first()
        if not user:
            click.echo(f"{username} not found on tenant {tenant_model.slug}")
            return
        user.password = generate_password_hash(secrets.token_urlsafe(32))
        db.session.commit()
        click.echo(f"Default password disabled for {username} on tenant {tenant_model.slug}")

    @app.cli.command()
    @click.option('--slug', required=True)
    @click.option('--name', default=None)
    @click.option('--domain', default=None)
    def add_tenant(slug, name, domain):
        """Adds a new tenant to the database"""
        tenant = get_or_create_tenant(slug=slug, name=name, domain=domain)
        click.echo(f"Tenant ready: {tenant.slug}")
