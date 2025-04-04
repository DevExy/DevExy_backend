import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

# PostgreSQL Azure connection settings
POSTGRES_HOST = os.environ.get("PGHOST", "devexy-db.postgres.database.azure.com")
POSTGRES_USER = os.environ.get("PGUSER", "user")
POSTGRES_PORT = os.environ.get("PGPORT", "5432")
POSTGRES_DB = os.environ.get("PGDATABASE", "postgres")
POSTGRES_PASSWORD = os.environ.get("PGPASSWORD", "")

# Create PostgreSQL connection URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Context manager for database operations
@contextmanager
def get_db_connection():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        print(f"Database connection error: {e}")
        raise
    finally:
        db.close()

# Dependency to get database session
def get_db():
    with get_db_connection() as db:
        yield db