"""
Database connection and session management.
Supports both PostgreSQL (Docker) and SQLite (local development).
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator, AsyncGenerator
from app.core.config import settings

# Create SQLAlchemy engine
# Get database URL from settings (supports both PostgreSQL and SQLite)
database_url = settings.sync_database_url

# Configure engine parameters based on database type
engine_args = {
    "pool_pre_ping": True,
}

# Add connection pool settings only for PostgreSQL
if "postgresql" in database_url:
    engine_args.update({
        "pool_size": 10,
        "max_overflow": 20,
    })
elif "sqlite" in database_url:
    # SQLite specific settings
    engine_args.update({
        "connect_args": {"check_same_thread": False}  # Required for SQLite with FastAPI
    })

engine = create_engine(database_url, **engine_args)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create async engine and session for async operations
async_database_url = database_url.replace('sqlite:///', 'sqlite+aiosqlite:///')
if "postgresql" in database_url:
    async_database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')

async_engine = create_async_engine(async_database_url, **engine_args)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    
    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async dependency to get database session.
    
    Yields:
        AsyncSession: SQLAlchemy async database session
    """
    async with AsyncSessionLocal() as session:
        yield session
