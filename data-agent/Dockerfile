# ─── build image ──────────────────────────────────────────────────────────────
FROM python:3.11-slim

RUN apt-get update && apt-get install -y build-essential curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8501
HEALTHCHECK CMD curl -fs http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app/ui_streamlit.py", "--server.address=0.0.0.0", "--server.port=8501"]

