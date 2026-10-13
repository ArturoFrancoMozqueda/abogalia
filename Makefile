PYTHON ?= python3
API_PYTHON = apps/api/.venv/bin/python
API_RUFF = apps/api/.venv/bin/ruff

.PHONY: api-install dev-api dev-web check check-api check-web

api-install:
	$(PYTHON) -m venv apps/api/.venv
	$(API_PYTHON) -m pip install --require-hashes -r apps/api/requirements-dev.txt

dev-api:
	$(API_PYTHON) -m uvicorn abogalia_api.main:app --app-dir apps/api/src --host 127.0.0.1 --port 8090 --reload --reload-dir apps/api/src

dev-web:
	pnpm dev:web

check: check-api check-web

check-api:
	$(API_RUFF) check apps/api
	$(API_RUFF) format --check apps/api
	$(API_PYTHON) -m pip check
	cd apps/api && PYTHONPATH=src .venv/bin/python -c "from abogalia_api.main import app; assert app.title == 'Abogalia API'"

check-web:
	pnpm check
