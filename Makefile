.PHONY: fastapi-dev build-layer build-function deploy db-up db-down db-migrate db-revision lint lint-ci typecheck check pre-commit

#----------------- Defaults -----------------
env_file ?= .env

#---------------- Dev Server ----------------
fastapi-dev: db-up
	uv run --env-file $(env_file) fastapi dev

#---------------- AWS Deploy ----------------
build-layer:
	rm -rf lambda-layer/python
	mkdir -p lambda-layer/python
	uv export --no-dev --no-hashes --format requirements-txt > requirements.txt
	uv pip install -r requirements.txt --target lambda-layer/python/ --python-platform linux --python-version 3.12
	rm requirements.txt

build-function:
	rm -rf .build/function
	mkdir -p .build/function
	cp -r apps .build/function/apps
	cp -r packages .build/function/packages

deploy:
	@bash scripts/make_sam_params.sh
	@make build-function
	sam build && sam deploy --parameter-overrides file:///tmp/sam_params.yaml

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

pre-commit: lint typecheck
	uv run pre-commit run --all-files
