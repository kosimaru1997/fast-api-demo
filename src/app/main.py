import asyncio

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.database import AsyncSessionLocal, init_db
from src.app.db.repository import repository_sample
from src.app.db.schema import model_schema_sample

if __name__ == "__main__":
    asyncio.run(init_db())

app = FastAPI()


# Dependency
# DBセッションを取得する関数を非同期に修正
async def get_db() -> AsyncSession:
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()


# Dependency
# こっちの書き方のほうが自動でトランザクションが管理されて良さそう
# (うそです。リクエスト終了時にwith句が閉じてコミットされるが、ディスク書き込みが遅い場合はレスポンスの直前に書き込みが行われるのでダメそう)
# async def get_db() -> AsyncSession:
#     async with AsyncSessionLocal() as db:
#         async with db.begin():
#             yield db  # DBセッションを返す


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/users/", response_model=model_schema_sample.User)
async def create_user(user: model_schema_sample.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = repository_sample.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return repository_sample.create_user(db=db, user=user)


@app.get("/users/", response_model=list[model_schema_sample.User])
def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    users = repository_sample.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=model_schema_sample.User)
def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    db_user = repository_sample.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=model_schema_sample.Item)
def create_item_for_user(
        user_id: int, item: model_schema_sample.ItemCreate, db: AsyncSession = Depends(get_db)
):
    return repository_sample.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[model_schema_sample.Item])
def read_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    items = repository_sample.get_items(db, skip=skip, limit=limit)
    return items
