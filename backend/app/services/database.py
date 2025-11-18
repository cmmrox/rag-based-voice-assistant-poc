import logging
from typing import AsyncGenerator
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

logger = logging.getLogger(__name__)

# SQLAlchemy Base for models
Base = declarative_base()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=False,  # Set to True for SQL query logging during development
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to get database session.

    Usage in FastAPI routes:
        @router.post("/endpoint")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}", exc_info=True)
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_database_connection() -> dict:
    """
    Check database connectivity for health checks.

    Returns:
        dict: Status information about database connection
    """
    try:
        async with AsyncSessionLocal() as session:
            # Execute a simple query to check connection
            await session.execute(text("SELECT 1"))

            logger.info("Database connection successful")
            return {
                "status": "connected",
                "database": "PostgreSQL",
                "url": settings.database_url.split("@")[-1]  # Hide credentials
            }

    except Exception as e:
        logger.error(f"Database connection failed: {e}", exc_info=True)
        return {
            "status": "error",
            "database": "PostgreSQL",
            "error": str(e)[:100]
        }


async def init_db():
    """
    Initialize database - create all tables.
    This should typically be done via Alembic migrations in production.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}", exc_info=True)
        raise
