# Developer Setup Guide for Dummies

This document explains how to run and develop the Data Agent locally.
It assumes minimal knowledge of Python and Docker.

## 1. Requirements

- Python 3.11 installed on your system.
- `git` command line tools.
- (Optional) Docker if you want to build the containers.

## 2. Clone the repository

```powershell
git clone https://github.com/your-org/data-agent.git
cd data-agent
```

## 3. Create a virtual environment

```powershell
python -m venv .venv
\.\.venv\Scripts\Activate.ps1
pip install -r data-agent/requirements.txt -r requirements-dev.txt
```

The first command creates an isolated Python environment so that
packages do not interfere with your system. The second activates it and
installs all runtime and development dependencies.

## 4. Run the API server

While the virtual environment is active, start the FastAPI server:

```powershell
uvicorn app.api:app --reload
```

Navigate to `http://localhost:8000/docs` to see the interactive API docs.
The `--reload` flag automatically restarts the server when you modify
files under `app/`.

## 5. Frontend development

The React UI lives in the `frontend/` folder.

```powershell
cd frontend
npm install
npm run dev
```

The development server listens on port `5173` by default. Visit
`http://localhost:5173` to open the UI.

## 6. Running tests

From the repository root run:

```powershell
$env:PYTHONPATH = '.'
pytest -q
```

You may need to activate the virtual environment first.

## 7. Useful Makefile commands

A few helper targets are defined in the `Makefile`:

- `make dev` – start the API with reload (requires venv).
- `make lint` – run code style checks using pre-commit.
- `make fmt` – auto-format the code base.
- `make docker` – build and run the Docker compose stack.

On Windows you may need to install `make` separately (e.g. via
[Chocolatey](https://chocolatey.org/) or the
[GnuWin](http://gnuwin32.sourceforge.net/packages/make.htm) package) or
run the commands inside the file manually.

## 8. Common issues

- **Missing dependencies** – double check that you activated the
  virtual environment before installing packages.
- **Port already in use** – change the `API_PORT` or `FRONTEND_PORT`
  environment variables in the `.env` file.
- **Tests cannot import modules** – make sure `PYTHONPATH` includes the
  repository root (`.`) when running pytest.

Happy hacking!
