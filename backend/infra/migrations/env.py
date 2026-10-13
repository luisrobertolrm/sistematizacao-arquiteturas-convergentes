from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from infra.configurations import metadata
from infra.database.settings import DatabaseSettings

if context.config.config_file_name:
    fileConfig(context.config.config_file_name)


def offline() -> None:
    context.configure(
        url=DatabaseSettings().database_url.get_secret_value(),
        target_metadata=metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def online() -> None:
    engine = create_engine(
        DatabaseSettings().database_url.get_secret_value(),
        poolclass=pool.NullPool,
        hide_parameters=True,
    )
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    offline()
else:
    online()
