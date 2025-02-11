from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import DATABASE_URL


engine = create_async_engine(
    DATABASE_URL,
    echo=False,  #!! off in prod
    future=True,
)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_db():
    async with async_session() as session:
        yield session
