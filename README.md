# Data Summarization & Charting Agent

Offline-first tool that lets a user drop CSV or Excel files, ask natural language questions, and instantly get summaries or publication-ready charts. All computation, storage and LLM inference stay on the local machine.

---

## 1. Problem Statement

Teams often need quick exploratory analysis without sending sensitive data to the cloud. Analysts waste time writing repetitive pandas code or plotting boilerplate. This project provides a local UI that understands a user question and generates the right pandas operations and matplotlib charts automatically.

---

## 2. Core Capabilities (Target)

### 2.1 MVP (Phase 1)

- Upload CSV or XLSX up to a configurable size.
- Preview head, column types and null counts.
- Basic descriptive stats and summaries.
- Manual chart builder for common plots: line, bar, histogram, box, scatter.
- Download charts as PNG and tables as CSV.

### 2.2 Natural Language Layer (Phase 2)

- Ask: "Show sales trend for last 3 months" or "Summarise revenue by region".
- Local LLM parses intent and generates safe pandas + matplotlib code.
- Sandbox execution with guardrails (AST checks, allowed API whitelist).

### 2.3 Convenience Features (Phase 3)

- Auto date parsing and time range helpers.
- Column suggestion and type coercion hints.
- Chart theming presets and dark/light toggle.
- Session history of prompts, code and outputs.
- One click export of a report (PDF or PPTX) with charts and key stats.

### 2.4 Optional Extras (Phase 4)

- Vector store (ChromaDB or FAISS) to remember previously analysed files.
- Multi file join and compare workflows.
- Plug-in system for custom transforms or domain templates (finance, retail, logistics).
- Role based access on a LAN deployment (FastAPI backend + auth).

---

## 3. Tech Stack

| Layer       | Choice (initial)                               | Notes                                                |
| ----------- | ---------------------------------------------- | ---------------------------------------------------- |
| UI          | React (Vite + MUI)                             | Modern web frontend. |
| Data engine | pandas, numpy                                  | Mature ecosystem.                                    |
| Charts      | matplotlib                                     | Requirement. Others optional later (plotly, altair). |
| LLM runtime | llama.cpp or ollama                            | Runs Mistral, Phi, Qwen etc locally.                 |
| Code runner | Python sandbox (restricted exec or subprocess) | Prevent arbitrary code execution.                    |
| Packaging   | Docker, docker compose                         | Deterministic environment.                           |
| Dev comfort | VS Code Dev Containers or local venv           | Your choice.                                         |

---

## 4. High Level Architecture

1. **Frontend (React)**
   - React app with file uploader, prompt box, chart and table viewers.
2. **Controller**
   - Routes user intent: direct UI selections or NL prompt.
3. **LLM Interpreter** (Phase 2)
   - Prompt template + few shot examples -> pandas/matplotlib code.
4. **Safe Executor**
   - Static analysis of code AST.
   - Execute in a jailed namespace with only approved imports.
5. **Result Renderer**
   - DataFrame -> table, fig -> PNG buffer.
6. **Persistence**
   - Cache datasets and generated artifacts in local folders.

---

## 5. Typical User Flow

1. User drops `sales_aug.xlsx`.
2. App shows preview and summary.
3. User types: "Compare average bill amount by region for Q2".
4. LLM returns Python snippet. Safe executor runs it.
5. App displays a bar chart and a summary table.
6. User downloads the PNG and the CSV.

---

## 6. Getting Started

### 6.1 Prerequisites

- Docker Desktop or Docker Engine
- VS Code (optional)
- For local run without Docker: Python 3.11

### 6.2 One line Docker run

```bash
docker compose up --build
```

Backend will be available at [http://localhost:8000](http://localhost:8000)
and the React UI at [http://localhost:3000](http://localhost:3000)

### 6.3 Local venv (no Docker)

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r data-agent/requirements.txt
uvicorn app.api:app --reload
cd frontend && npm install && npm run dev
```

### 6.4 Makefile Shortcuts

```bash
# run local app with venv
make dev

# format and lint
make fmt
make lint

# run docker compose
make docker
```


### 6.5 FastAPI server

```bash
uvicorn app.api:app --reload
```

This exposes endpoints like `/upload`, `/summary/{id}`, `/chart/{id}`, `/nl2code/{id}` and `/run_code/{id}`.

### 6.6 Running tests

Install the runtime and dev requirements first:

```bash
pip install -r data-agent/requirements.txt -r requirements-dev.txt
```

Then execute the test suite with the repository root on the `PYTHONPATH`:

```bash
PYTHONPATH=. pytest -q
```

---

## 7. Repository Layout

```
root/
├── app/
│   └── core/
│       ├── file_loader.py     # CSV/XLSX ingestion
│       ├── analysis.py        # Simple summaries
│       ├── charts.py          # Matplotlib rendering helpers
│       └── llm_driver.py      # NL -> code bridge (placeholder)
├── data/                      # User uploaded data (gitignored)
├── docker-compose.yml
├── data-agent/
│   ├── requirements.txt
│   └── Dockerfile.api
└── README.md
```

---

## 8. Roadmap Checklist

- **Data Prep Wizards**
  - Column type fixer (int/float/date)
  - Missing value heatmap
  - Quick outlier detection (IQR / z-score)
- **Chart UX**
  - Themes (dark/light)
  - Save chart presets
  - Facet grids for bar/hist in addition to line

---

## 9. Local LLM Integration Plan (Sketch)

1. Run `ollama run mistral:7b-instruct` or llama.cpp server.
2. Prompt template:
   - System: "You translate English questions into safe pandas and matplotlib code. Only use columns provided."
   - Few shot examples mapping question -> code.
3. Parse model output, strip fenced code.
4. Validate AST for allowed nodes (Import, Call, Assign, etc.).
5. Execute and capture DataFrame or Figure objects.
6. Return result to UI.
7. Cache previous questions and reuse answers when possible.
8. Include recent conversation history in the prompt for better context.

---

## 10. Security and Safety Notes

- Never execute arbitrary code from the model without checks.
- No internet calls from within analysis code.
- Uploaded data never leaves the host unless user exports it.
- Option to run in an air gapped machine.

---

## 11. Contribution Guidelines (future)

- Use conventional commits. Example: `feat: add histogram chart`
- Open an issue before large feature work.
- Write small tests for any pure functions in `core`.

---

## 12. License

Choose a permissive OSS license (MIT or Apache-2.0) unless you have constraints. Add `LICENSE` file accordingly.

---

## 13. Credits

Initial concept and implementation:&#x20;

---
## 14. React UI Prototype

An experimental React + Vite frontend lives under `frontend/`. It uses
MUI components together with Recharts for interactive charts. Run `npm install` and then `npm run dev` inside that directory to start
the development server.


Happy building.

