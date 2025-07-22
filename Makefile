VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

$(VENV)/bin/activate: requirements-dev.txt data-agent/requirements.txt
	python -m venv $(VENV)
	$(PIP) install -r data-agent/requirements.txt -r requirements-dev.txt
	touch $@

.PHONY: dev docker lint fmt test

dev: $(VENV)/bin/activate
	$(VENV)/bin/streamlit run data-agent/app/ui_streamlit.py

docker:
	docker compose -f data-agent/docker-compose.yml up --build

lint:
	$(VENV)/bin/pre-commit run --files $(shell git ls-files '*.py')

fmt:
	$(VENV)/bin/pre-commit run ruff-format isort pyproject-fmt --files $(shell git ls-files '*.py' 'pyproject.toml')

test: $(VENV)/bin/activate
	$(PYTHON) -m pytest
