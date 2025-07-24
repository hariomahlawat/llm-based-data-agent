# Offline Deployment Guide for Dummies (Windows Server)

This guide walks through running the Data Summarization & Charting Agent on an
**air‑gapped** Windows Server machine using Docker. Every step is spelled out so
that even first‑time Docker users can follow along.

## 1. Prepare on an Internet‑Connected Machine

1. **Install Docker Desktop** on any machine with internet access.
2. **Clone this repository** and open a terminal in the repo root.
3. Download all container images you will need:
   ```powershell
   docker pull python:3.11-slim
   docker pull node:20-alpine
   docker pull nginx:alpine
   docker pull ollama/ollama:latest
   ```
4. Save these images to tar archives so you can move them offline:
   ```powershell
   docker save -o python.tar python:3.11-slim
   docker save -o node.tar node:20-alpine
   docker save -o nginx.tar nginx:alpine
   docker save -o ollama.tar ollama/ollama:latest
   ```
5. Create the directory `wheels` inside `data-agent/` and download Linux
   wheels for Python 3.11. Use the `--platform` option so that the packages
   work inside the Linux based Docker container:
   ```powershell
   mkdir data-agent\wheels
   pip download --platform manylinux2014_x86_64 --python-version 3.11 \
       --only-binary=:all: -r data-agent\requirements.txt -d data-agent\wheels
   ```
6. (Optional) Cache npm packages for the frontend build:
   ```powershell
   mkdir frontend\npm_cache
   npm install --ignore-scripts --cache ./frontend/npm_cache
   ```
7. Copy the entire repository folder together with the `*.tar` files to your
   offline Windows Server machine (USB drive or other secure method).

## 2. Set Up the Offline Windows Server

1. **Install Docker** on the Windows Server. Docker Desktop or Docker Engine is
   fine. Reboot if required.
2. Load the images you previously saved:
   ```powershell
   docker load -i python.tar
   docker load -i node.tar
   docker load -i nginx.tar
   docker load -i ollama.tar
   ```
3. Ensure Docker is working by running `docker images`.

## 3. Build the Containers Offline

1. Open PowerShell and change to the repository directory.
2. Build the API container:
   ```powershell
   cd data-agent
   docker build -t data-agent-api .
   cd ..
   ```
   The Dockerfile checks for a local `wheels` folder and installs packages from
   there without contacting the internet.
3. Build the frontend container:
   ```powershell
   cd frontend
   docker build -t data-agent-frontend .
   cd ..
   ```
   If you created the optional `npm_cache` directory, the build will run in
   offline mode.

## 4. Start the Stack

1. In the repo root run:
   ```powershell
   docker compose up
   ```
2. Copy `.env.example` to `.env` if you need to tweak ports or paths. The
   compose file reads all configuration from this file.
3. The API will listen on port `8000` and the React UI on `3000`. The optional
   `proxy` service exposes both on `http://localhost:8080`.
4. To stop everything press `Ctrl+C` and then run `docker compose down`.

## 5. Common Hurdles

- **Port already in use** – change the ports in `docker-compose.yml` if 8000 or
  3000 are taken.
- **File access denied** – ensure your current user has permission to write to
  the project directory where Docker stores data volumes.
- **Image not found** – verify that you loaded all `*.tar` files with
  `docker load`.
- **Package install fails during build** – make sure the `wheels` directory
  contains all `.whl` files from `pip download` and that you preserved directory
  structure when copying.
- **Frontend build errors offline** – if you skipped the optional npm cache,
  Node will try to reach the internet. Create the cache as described in section
  1 step 6.

## 6. Updating the Application

When you have internet access again, repeat the preparation steps on an online
machine to fetch updated images or dependencies, then copy them to the server and
rebuild.

That's it! You now have a completely offline Dockerized deployment running on
Windows Server.
