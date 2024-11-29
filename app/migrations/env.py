"""
Alembic environment configuration for database migrations.

This script initializes the Alembic context, configures metadata for migrations,
and defines functions to run migrations in both online and offline modes.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from db.models import Base

# This is the Alembic Config object, which provides access to the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here for 'autogenerate' support.
# This references the SQLAlchemy Base metadata for Alembic to detect changes.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    allowing migrations to be run without requiring a live database
    connection.

    Calls to context.execute() emit the given string to the script output.
    """
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
    """
    Run migrations in 'online' mode.

    In this scenario, an Engine is created, and a connection is associated
    with the context to apply the migrations directly to a live database.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


# Determine whether the migrations should run in offline or online mode.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
