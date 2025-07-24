# Offline Deployment Guide (Linux/macOS)

This document explains how to run the Docker stack on a machine
without internet access. The process is similar to the Windows steps but
uses standard Linux commands.

## 1. Prepare on a machine with internet

1. Install Docker on an online machine.
2. Clone this repository and switch into it.
3. Pull all required container images:
   ```bash
   docker pull python:3.11-slim
   docker pull node:20-alpine
   docker pull nginx:alpine
   docker pull ollama/ollama:latest
   ```
4. Save the images to tar files for transfer:
   ```bash
   docker save -o python.tar python:3.11-slim
   docker save -o node.tar node:20-alpine
   docker save -o nginx.tar nginx:alpine
   docker save -o ollama.tar ollama/ollama:latest
   ```
5. Download Python packages to `data-agent/wheels`:
   ```bash
   mkdir -p data-agent/wheels
   pip download -r data-agent/requirements.txt -d data-agent/wheels
   ```
6. (Optional) cache npm packages for the frontend:
   ```bash
   mkdir -p frontend/npm_cache
   npm install --ignore-scripts --cache ./frontend/npm_cache
   ```
7. Copy the repository along with all `*.tar` files to the offline
   machine using a USB drive or other secure method.

## 2. Set up the offline host

1. Install Docker Engine on the target machine.
2. Load the saved images:
   ```bash
   docker load -i python.tar
   docker load -i node.tar
   docker load -i nginx.tar
   docker load -i ollama.tar
   ```
3. Confirm the images are available with `docker images`.

## 3. Build and run

1. Build the API container (installs packages from the `wheels` folder):
   ```bash
   cd data-agent
   docker build -t data-agent-api .
   cd ..
   ```
2. Build the frontend container:
   ```bash
   cd frontend
   docker build -t data-agent-frontend .
   cd ..
   ```
3. Start the full stack:
   ```bash
   docker compose up
   ```
   The API listens on port `8000` and the UI on `3000`. You can also use
   the optional `proxy` service which exposes both through port `8080`.

## 4. Common problems

- **"package not found" during build** – ensure the `wheels` directory
  contains all required `.whl` files from the online machine.
- **Docker cannot access files** – verify that the repository path is
  readable by your user and that SELinux/AppArmor is not blocking
  container mounts.
- **Ports already used** – change the values in `.env` and restart
  `docker compose`.
- **Ollama model missing** – on the online machine run
  `ollama pull mistral:7b-instruct` (or any model you want) and export it
  with `ollama export`, then copy the resulting files into the
  `ollama_data` volume on the offline host.

Once everything is up you can open `http://localhost:8080` (or the
individual service ports) in your browser.
