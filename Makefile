.PHONY: fastapi-dev db-up db-down db-migrate db-revision lint lint-ci typecheck check pre-commit

#----------------- Defaults -----------------
env_file ?= .env

#---------------- Dev Server ----------------
fastapi-dev: db-up
	uv run --env-file $(env_file) fastapi dev


#----------------- Database -----------------
db-up:
	docker compose --env-file $(env_file) up -d database

db-down:
	docker compose down database

db-migrate:
	uv run --env-file $(env_file) alembic upgrade head

db-revision:
	uv run --env-file $(env_file) alembic revision --autogenerate -m "$(msg)"

#--------------- Code quality ---------------
lint:
	uv run ruff format .
	uv run ruff check --fix .

lint-ci:
	uv run ruff format --check .
	uv run ruff check .

typecheck:
	uv run mypy packages/ apps/

check: lint-ci typecheck

pre-commit:
	uv run pre-commit run --all-files
