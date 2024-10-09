## FastAPI + SQLAlchemy

- セッションの開始と終了
    - リクエストごとにセッションを開始して、リクエスト終了時にセッションを閉じる(原則1リクエスト1セッション)
  ```python
  async def get_db() -> AsyncSession:
      db = AsyncSessionLocal()
      try:
          yield db
      finally:
          await db.close()
  ```
- トランザクションなしのクエリ
    - 特に考慮する必要なし、セッションを使用してクエリを実行するだけ
  ```python
  async def get_items(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(model_sample.Item).offset(skip).limit(limit))
    return result.scalars().all()
  ```
- トランザクションありのクエリ
    - with句を使用してトランザクションを開始し、トランザクション内でクエリを実行する。with句の終了時にトランザクションがコミットされるはず
  ```python
  async def create_user(user: model_schema_sample.UserCreate, db: AsyncSession):
      # ユーザーの作成処理
      db_user = model_sample.User(email=user.email, hashed_password=user.password)
      db.add(db_user)
      
      # コミット前(ディスク書き込み前)だけどDBメモリ上の最新状態になるはず？
      await db.refresh(db_user)
      return db_user
  
  async def some_function(user: model_schema_sample.UserCreate, db: AsyncSession):  
    # 呼び出し(コミットされるのは、with句の終了時、with句内でエラーが発生した場合はロールバックされるはず)
    async with db.begin():
      user = await create_user(user, db)
    ```

## Alembic(migration)

- 設定ファイルの生成

```sh
#alembic init alembic
alembic init -t async migration # for asynchronous support 非同期使う場合はこっち
```

- alembic.iniファイルにて、DBドライバ指定

```ini
sqlalchemy.url = {ドライバURLを指定}
```

- env.pyのモデル指定
    - note!: from src.app.db.models.model_sample import User, Itemのように対象のモデルのインポートを文が必要

```python
# note! ここにimport文を追加
from src.app.db.models.model_sample import User, Item

target_metadata = Base.metadata
```

- コマンド
    - マイグレーションファイルの生成(versionsディレクトリにファイルが生成される)
  ```sh
    alembic revision --autogenerate -m "some comment"
  ```
    - 最新のマイグレーションファイルが適用前だとエラーになる
    ```sh
      root@f7f40cc3cbec:/opt/project/src/app# alembic revision --autogenerate -m "add cloumn to user table"
      INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
      INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
      ERROR [alembic.util.messaging] Target database is not up to date.
     ```
    - migrationファイルの適用
  ```sh
    # 全マイグレーションファイル適用
    alembic upgrade head
    # 特定のマイグレーションファイル適用
    # Any time we need to refer to a revision number explicitly, we have the option to use a partial number. As long as this number uniquely identifies the version, it may be used in any command in any place that version numbers are accepted:
    alembic upgrade 668
    # 件数で指定もできる(現在の最新のマイグレーションファイルから指定した数だけ適用)
    alembic upgrade +2
    alembic downgrade -1
    alembic upgrade 668+2
  ```
    - 最新のマイグレーション

        - 現在の実行状況確認
  ```sh
    # 現在の状態確認
    alembic current
    # マイグレーション履歴の表示
    alembic history
  ```
    - ダウングレード
      ```sh
      # 全消し
      alembic downgrade base
      # 特定のマイグレーションファイルまで
      alembic downgrade 668
      ```
  ### SQLModelを使う場合
    - テーブル例
  ```python
  class UserSecond(SQLModel, AsyncAttrs, table=True):
    __tablename__ = "users_second"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(max_length=100, unique=True, index=True)
    hashed_password: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    # added_column: str = Field(default="default_value", max_length=255)

    items: List["ItemSecond"] = Relationship(back_populates="owner")


  class ItemSecond(SQLModel, AsyncAttrs, table=True):
      __tablename__ = "items_second"
  
      id: Optional[int] = Field(default=None, primary_key=True)
      title: str = Field(max_length=100, index=True)
      description: str = Field(max_length=255, index=True)
      owner_id: Optional[int] = Field(default=None, foreign_key="users_second.id")
  
      owner: Optional[UserSecond] = Relationship(back_populates="items")
  ```

    - env.pyのターゲット指定をSQLModelのモデルに変更
  ```python
  from src.app.db.models.model_sample import User, Item, UserSecond, ItemSecond
  
  target_metadata = SQLModel.metadata
  ```

    - script.py.makoのテンプレートにSQLModelのモデルを追加
  ```mako
  from alembic import op
  import sqlmodel <- 追加
  import sqlalchemy as sa
  ${imports if imports else ""}
  ```

## Poetry

- パッケージ管理ツール
    - 依存関係の解決をしつつライブラリのインストールをしてくれたりする
    - tool.poetry.dev-dependenciesみたいな感じで、特定の環境で使用するパッケージを1ファイルで指定できるが良いかな
    - パッケージ公開したいときに便利っぽい(使用予定はないけど)

pipだけでも良いけど、FastAPIで色々とライブラリを入れるときに依存関係が複雑になる可能性があるので使用してみる

## 初回サーバー起動前(初回にDockerfileから作成するときの手順)

下記の部分をコメントアウトしておく(初回はpoetry関連のファイルは存在しないため)

```sh
COPY ./src/pyproject.toml* .src/sorcpoetry.lock* ./src/

RUN poetry lock
RUN poetry install --no-root --with dev
```

```sh
docker-compose run \
--entrypoint "poetry init \
--name fast-api-demo \
--dependency fastapi \
--dependency uvicorn[standard]" \
api
```

```sh
docker-compose run \
--entrypoint "poetry install" \
api
```

## 気をつけるところ

#### PyCharmでFastAPI起動

- uvicornオプションを `--reload --host="0.0.0.0"` にすること
  (`--host="0.0.0.0`を入れないと`ホスト -> Dockerコンテナ -> エンドポイント`の通信ができない)

## Docs

### FastAPI

#### デバック設定

- https://fastapi.tiangolo.com/tutorial/debugging/#run-your-code-with-your-debugger

#### Poetryを利用したDockerイメージ

- https://fastapi.tiangolo.com/ja/deployment/docker/#_16

#### RDB関連

- SqlAlchemy: https://medium.com/@tclaitken/setting-up-a-fastapi-app-with-async-sqlalchemy-2-0-pydantic-v2-e6c540be4308
- Alembic: https://alembic.sqlalchemy.org/en/latest/tutorial.html

