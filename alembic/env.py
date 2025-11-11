# alembic/env.py
import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- ADD THESE IMPORTS ---
# This adds the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Import your settings and the Base metadata from your models
from app.config import settings
from app.models import Base
# --- END OF ADDED IMPORTS ---

# this is the Alembic Config object
config = context.config

# --- ADD THIS LINE ---
# Tell Alembic to use the DATABASE_URL from our settings
config.set_main_option("sqlalchemy.url", settings.database_url)
# --- END OF ADDED LINE ---

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

# ... other default functions remain the same ...
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
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()