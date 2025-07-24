VENV=.venv

ifeq ($(OS),Windows_NT)
    VENV_BIN=$(VENV)/Scripts
    PYTHON=$(VENV_BIN)/python.exe
    PIP=$(VENV_BIN)/pip.exe
    ACTIVATE=$(VENV_BIN)/activate
else
    VENV_BIN=$(VENV)/bin
    PYTHON=$(VENV_BIN)/python
    PIP=$(VENV_BIN)/pip
    ACTIVATE=$(VENV_BIN)/activate
endif

$(ACTIVATE): requirements-dev.txt data-agent/requirements.txt
	python -m venv $(VENV)
	$(PIP) install -r data-agent/requirements.txt -r requirements-dev.txt
	touch $@

.PHONY: dev docker lint fmt test

dev: $(ACTIVATE)
	$(VENV_BIN)/uvicorn app.api:app --reload

docker:
	docker compose up --build

lint:
	$(VENV_BIN)/pre-commit run --files $(shell git ls-files '*.py')

fmt:
	$(VENV_BIN)/pre-commit run ruff-format isort pyproject-fmt --files $(shell git ls-files '*.py' 'pyproject.toml')

test: $(ACTIVATE)
	$(PYTHON) -m pytest
