.PHONY: install lint test build dev

install:
	cd frontend && npm install
	cd backend && pip install -e ".[dev]"

lint:
	cd frontend && npm run lint
	cd backend && ruff check .
	cd backend && mypy src

test:
	cd frontend && npm run test
	cd backend && pytest

build:
	cd frontend && npm run build

dev:
	docker compose up
