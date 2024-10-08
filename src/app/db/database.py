from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "mysql+aiomysql://iimon:iimon@mysql:3306/iimon"

async_engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, echo=True
)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)

Base = declarative_base()


# 非同期コンテキストマネージャを使用(テーブル作成)
async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
