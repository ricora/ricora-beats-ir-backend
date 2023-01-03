# ricora-beats-ir-backend

<div>
  <a href="https://www.python.org/" alt="Python">
    <img src="https://img.shields.io/badge/-Python-3776ab?logo=python&logoColor=white" />
  </a>
  <a href="https://fastapi.tiangolo.com/" alt="FastAPI">
    <img src="https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white" />
  </a>
  <a href="https://docs.pydantic.dev/" alt="Pydantic">
    <img src="https://img.shields.io/badge/-Pydantic-e21f60" />
  </a>
  <a href="https://www.sqlalchemy.org/" alt="SQLAlchemy">
    <img src="https://img.shields.io/badge/-SQLAlchemy-ce2115" />
  </a>
  <a href="https://www.uvicorn.org/" alt="Uvicorn">
    <img src="https://img.shields.io/badge/-Uvicorn-4051b5" />
  </a>
  <a href="https://fly.io/" alt="Fly.io">
    <img src="https://img.shields.io/badge/-Fly.io-8b5cf6" />
  </a>
</div>

[RICORA Beats](https://github.com/RICORA/ricora-beats)のスコアランキングの管理Webサーバー。

## Development

### Set environment variable

```sh
export SECRET_KEY="mysecretkey"
export DATABASE_URL="postgresql://user:password@example.com:5432/database"
```

### Run development server

#### For Docker

```sh
docker compose up
```

#### For Vanilla Python + venv

```sh
pip install -r requirements.txt
cd ./app/
uvicorn main:app --reload --port 8080
```
