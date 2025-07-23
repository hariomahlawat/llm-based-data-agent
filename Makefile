VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

$(VENV)/bin/activate: requirements-dev.txt data-agent/requirements.txt
	python -m venv $(VENV)
	$(PIP) install -r data-agent/requirements.txt -r requirements-dev.txt
	touch $@

.PHONY: dev docker lint fmt test

dev: $(VENV)/bin/activate
    $(VENV)/bin/uvicorn app.api:app --reload

docker:
	docker compose up --build

lint:
	$(VENV)/bin/pre-commit run --files $(shell git ls-files '*.py')

fmt:
	$(VENV)/bin/pre-commit run ruff-format isort pyproject-fmt --files $(shell git ls-files '*.py' 'pyproject.toml')

test: $(VENV)/bin/activate
	$(PYTHON) -m pytest
