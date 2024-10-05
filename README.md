
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


## Docs

### FastAPI

#### デバック設定
- https://fastapi.tiangolo.com/tutorial/debugging/#run-your-code-with-your-debugger

#### Poetryを利用したDockerイメージ
- https://fastapi.tiangolo.com/ja/deployment/docker/#_16