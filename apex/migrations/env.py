from logging.config import fileConfig

from flask import current_app

from alembic import context

config = context.config

fileConfig(config.config_file_name)
target_db = current_app.extensions["migrate"].db


def get_engine():
    try:
        return target_db.get_engine()
    except TypeError:
        return target_db.engine


def get_engine_url():
    return get_engine().url.render_as_string(hide_password=False).replace("%", "%%")


config.set_main_option("sqlalchemy.url", get_engine_url())
target_metadata = target_db.metadata


def process_revision_directives(context, revision, directives):
    if getattr(config.cmd_opts, "autogenerate", False):
        script = directives[0]
        if script.upgrade_ops.is_empty():
            directives[:] = []


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    conf_args = current_app.extensions["migrate"].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, **conf_args)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
