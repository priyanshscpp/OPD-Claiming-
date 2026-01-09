from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

# Create the SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # Ensures connections are valid
    echo=False                # Disable SQL echo logs
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()


# Dependency for FastAPI routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# OPTIONAL: create tables programmatically (if not using Alembic)
def init_db():
    """
    Creates all tables defined in SQLAlchemy models.
    Useful for Railway deployment when a DB starts empty.
    """
    Base.metadata.create_all(bind=engine)
