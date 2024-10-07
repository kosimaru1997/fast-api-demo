from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select  # 非同期で使用するために必要

from src.app.db.models import model_sample
from src.app.db.schema import model_schema_sample


# ユーザーをIDで取得
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(model_sample.User).where(model_sample.User.id == user_id))
    return result.scalars().first()


# メールアドレスでユーザーを取得
async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(model_sample.User).where(model_sample.User.email == email))
    return result.scalars().first()


# ユーザーをスキップ・リミットで取得
async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(model_sample.User).offset(skip).limit(limit))
    return result.scalars().all()


# ユーザーを作成
async def create_user(db: AsyncSession, user: model_schema_sample.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = model_sample.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


# アイテムをスキップ・リミットで取得
async def get_items(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(model_sample.Item).offset(skip).limit(limit))
    return result.scalars().all()


# ユーザーのアイテムを作成
async def create_user_item(db: AsyncSession, item: model_schema_sample.ItemCreate, user_id: int):
    db_item = model_sample.Item(**item.model_dump(), owner_id=user_id)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item
