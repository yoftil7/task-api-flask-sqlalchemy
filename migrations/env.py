import sys
import os

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure Alembic can import your Flask app
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app import create_app, db
from app.models import Task  # import models so Alembic knows them

# Alembic Config object
config = context.config

# Setup logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use Flask’s DB config instead of hardcoding in alembic.ini
flask_app = create_app()
with flask_app.app_context():
    config.set_main_option(
        "sqlalchemy.url", flask_app.config["SQLALCHEMY_DATABASE_URI"]
    )

# Target metadata from Flask-SQLAlchemy
target_metadata = db.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
