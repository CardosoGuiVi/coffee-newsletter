.PHONY: db-up db-down fastapi-dev lint lint-ci

db-up:
	docker compose --env-file .env up -d database

db-down:
	docker compose down database

fastapi-dev: db-up
	uv run --env-file .env fastapi dev

lint:
	uv run ruff format .
	uv run ruff check --fix .

lint-ci:
	uv run ruff format --check .
	uv run ruff check .
