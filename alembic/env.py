from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
import os
import json
from alembic import context

def load_config(env):
    with open(os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json'), 'r') as config_file:
        config = json.load(config_file)
        return config[env]

config = context.config

fileConfig(config.config_file_name)

environment = os.getenv('ENVIRONMENT', 'development')
db_config = load_config(environment)

config.set_main_option('sqlalchemy.url', f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")

target_metadata = None

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
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
