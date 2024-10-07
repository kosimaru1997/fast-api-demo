##################################################
# build image
##################################################
FROM python:3.12-slim-bookworm  AS requirements-stage

# ログのバッファリングを無効化(ログがリアルタイムに表示されるようにする)
ENV PYTHONUNBUFFERED 1
# コマンド実行時に、scr以下のmoduleに直接アクセスできるようにする
ENV PYTHONPATH "${PYTHONPATH}:/src"

WORKDIR /src
# pipを使ってpoetryをインストール
RUN pip install poetry

# poetryの定義ファイルをコピー
COPY ./src/pyproject.toml ./src/poetry.lock  /src/

# poetryが仮想環境を作成しないように設定
RUN poetry config virtualenvs.create false
RUN poetry config virtualenvs.in-project false

# 依存関係をrequirements.txtに出力 ハッシュを除外
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes





##################################################
# pycharm image(開発用)
##################################################
FROM requirements-stage AS pycharm

# SqlALchemyの非推奨メソッドの仕様による警告を表示
ENV SQLALCHEMY_WARN_20=1

RUN echo "pycharm"

WORKDIR /src

COPY ./src/app /src/app

## 依存関係をインストール
RUN poetry lock
RUN poetry install --no-root --with dev

# PyCharmのから起動するので、ENTRYPOINTは使用しない
#ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--reload"]


##################################################
# dev image
##################################################
FROM python:3.12-slim-bookworm AS dev

ENV PYTHONUNBUFFERED 1

RUN echo "dev"

WORKDIR /src

COPY --from=requirements-stage /src/requirements.txt /src/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt

COPY ./src/app /src/app

RUN addgroup --system iimon \
  && adduser --system --ingroup iimon iimon

USER iimon

ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
#ENTRYPOINT ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--workers", "4", "--log-level", "info"]

