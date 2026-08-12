.PHONY: install install-backend install-frontend dev-backend dev-frontend dev test health lint

AGENT_OS_PORT ?= 7777
BACKEND_BASE_URL ?= http://localhost:$(AGENT_OS_PORT)

install: install-backend install-frontend

install-backend:
	cd backend && uv sync

install-frontend:
	cd frontend && npm ci

dev-backend:
	cd backend/src && AGENT_OS_PORT=$(AGENT_OS_PORT) uv run --project .. python app.py

dev-frontend:
	cd frontend && npm run dev

dev:
	@echo "Run make dev-backend and make dev-frontend in separate terminals"

test:
	cd backend && BACKEND_BASE_URL=$(BACKEND_BASE_URL) uv run pytest tests/integration/test_status.py -m "not integration"

health:
	curl -sS "$(BACKEND_BASE_URL)/status"

lint:
	cd backend && uv run python -m compileall -q src tests
	cd frontend && npm run build
