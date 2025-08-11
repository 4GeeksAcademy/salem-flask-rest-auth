import logging
from logging.config import fileConfig
from flask import current_app
from alembic import context
from sqlalchemy import pool
from sqlalchemy.exc import SQLAlchemyError

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger('alembic.env')


def get_engine():
    """Get the database engine with proper error handling."""
    try:
        # Flask-SQLAlchemy >= 3.x
        if hasattr(current_app.extensions['migrate'].db, 'engine'):
            return current_app.extensions['migrate'].db.engine
        # Flask-SQLAlchemy < 3.x and Alchemical
        else:
            return current_app.extensions['migrate'].db.get_engine()
    except KeyError:
        raise RuntimeError("Flask-Migrate extension not found. Make sure Flask-Migrate is properly initialized.")
    except AttributeError as e:
        raise RuntimeError(f"Unable to access database engine: {e}")
    except Exception as e:
        logger.error(f"Unexpected error getting database engine: {e}")
        raise


def get_engine_url():
    """Get the database URL with proper formatting."""
    try:
        engine = get_engine()
        # Modern SQLAlchemy approach
        if hasattr(engine.url, 'render_as_string'):
            return engine.url.render_as_string(hide_password=False).replace('%', '%%')
        # Fallback for older versions
        else:
            return str(engine.url).replace('%', '%%')
    except Exception as e:
        logger.error(f"Failed to get engine URL: {e}")
        raise


def get_metadata():
    """Get the metadata object with version compatibility."""
    try:
        target_db = current_app.extensions['migrate'].db
        
        # Flask-SQLAlchemy >= 3.x with multiple bind support
        if hasattr(target_db, 'metadatas'):
            return target_db.metadatas[None]
        
        # Flask-SQLAlchemy < 3.x
        return target_db.metadata
        
    except Exception as e:
        logger.error(f"Failed to get metadata: {e}")
        raise


def validate_configuration():
    """Validate the Alembic configuration."""
    url = config.get_main_option("sqlalchemy.url")
    if not url:
        raise ValueError("Database URL not configured in alembic.ini")
    
    if not current_app:
        raise RuntimeError("No Flask application context available")
    
    if 'migrate' not in current_app.extensions:
        raise RuntimeError("Flask-Migrate not initialized")


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    try:
        validate_configuration()
        url = config.get_main_option("sqlalchemy.url")
        
        context.configure(
            url=url,
            target_metadata=get_metadata(),
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()
            
    except Exception as e:
        logger.error(f"Offline migration failed: {e}")
        raise


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    
    def process_revision_directives(context, revision, directives):
        """Prevent auto-migration when there are no changes."""
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No changes in schema detected.')

    try:
        validate_configuration()
        
        # Set the database URL for Alembic
        config.set_main_option('sqlalchemy.url', get_engine_url())
        
        # Get configuration arguments from Flask-Migrate
        conf_args = current_app.extensions['migrate'].configure_args.copy()
        
        # Set the revision directive processor if not already set
        if conf_args.get("process_revision_directives") is None:
            conf_args["process_revision_directives"] = process_revision_directives

        # Get the database engine
        connectable = get_engine()

        # Configure connection pooling for better performance
        if hasattr(connectable, 'pool') and connectable.pool:
            # Use connection pooling settings
            pass
        else:
            # Create engine with pooling if needed
            connectable = connectable.execution_options(
                isolation_level="AUTOCOMMIT"
            )

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=get_metadata(),
                compare_type=True,
                compare_server_default=True,
                **conf_args
            )

            with context.begin_transaction():
                context.run_migrations()
                
    except SQLAlchemyError as e:
        logger.error(f"Database error during migration: {e}")
        raise
    except Exception as e:
        logger.error(f"Online migration failed: {e}")
        raise


# Run the appropriate migration mode
try:
    if context.is_offline_mode():
        logger.info("Running migrations in offline mode")
        run_migrations_offline()
    else:
        logger.info("Running migrations in online mode")
        run_migrations_online()
except Exception as e:
    logger.error(f"Migration execution failed: {e}")
    raise