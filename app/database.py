from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import config


engine = create_async_engine(
    config.database_url,
    echo=False,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    from app.models import Appeal  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # Eski bazalarda reviewed_by bo‘lmasa qo‘shiladi
        await conn.execute(text("ALTER TABLE appeals ADD COLUMN IF NOT EXISTS reviewed_by BIGINT"))


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
