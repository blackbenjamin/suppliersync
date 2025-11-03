
# SupplierSync — Agentic AI Orchestrator (Wayfair-fit Demo)

A minimal, end-to-end demo of a multi‑agent system that simulates a Wayfair‑like sales ecosystem:
- **Supplier Agent**: publishes/updates SKUs, availability, and wholesale prices
- **Buyer/Pricing Agent**: curates catalog, sets prices, monitors margin & price competitiveness
- **CX Agent**: ingests incidents/returns and triggers root‑cause analysis & product feedback loops
- **Orchestrator**: schedules/coordinates agents; enforces governance; writes eval metrics
- **RAG Layer**: optional retrieval from supplier spec sheets (local PDFs/Markdown)
- **Observability/Governance**: prompt/response logging, guardrails, offline evals

## Quickstart

### Option 1: Direct execution
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env  # Fill OPENAI_API_KEY and SQLITE_PATH
python main.py
```

### Option 2: FastAPI service (recommended for dashboard)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env  # Fill OPENAI_API_KEY and SQLITE_PATH
uvicorn api:app --reload --port 8000
```

The API exposes:
- `GET /health` - Health check
- `POST /orchestrate` - Run one orchestration step

Optional dashboard steps are in `../dashboard/README.md`.
