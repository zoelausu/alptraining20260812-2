.PHONY: install install-backend dev-backend dev-frontend dev test health lint

AGENT_OS_PORT ?= 7777
BACKEND_BASE_URL ?= http://localhost:$(AGENT_OS_PORT)

install: install-backend

install-backend:
	cd backend && uv sync

dev-backend:
	cd backend/src && AGENT_OS_PORT=$(AGENT_OS_PORT) uv run --project .. python app.py

dev-frontend:
	@echo "Frontend not implemented yet — run /speckit-implement for frontend tasks (T010–T017)"

dev:
	@echo "Run make dev-backend (frontend pending)"

test:
	cd backend && BACKEND_BASE_URL=$(BACKEND_BASE_URL) uv run pytest tests/integration/test_status.py -m "not integration"

health:
	curl -sS "$(BACKEND_BASE_URL)/status"

lint:
	cd backend && uv run python -m compileall -q src tests
