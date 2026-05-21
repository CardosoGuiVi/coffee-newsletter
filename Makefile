.PHONY: db-up db-down fastapi-dev

db-up:
	docker compose --env-file .env up -d database

db-down:
	docker compose down database

fastapi-dev: db-up
	uv run --env-file .env fastapi dev
