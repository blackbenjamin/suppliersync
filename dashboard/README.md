
# SupplierSync Dashboard (Next.js)

Wayfair-style console over the same `../suppliersync.db` created by the Python demo.

## Prerequisites

1. **Start the FastAPI orchestrator service** (from `../suppliersync/`):
   ```bash
   cd ../suppliersync
   source .venv/bin/activate  # or activate your venv
   uvicorn api:app --reload --port 8000
   ```

2. **Configure environment**:
   ```bash
   cp env.local.example .env.local
   # Edit .env.local and set:
   # - SQLITE_PATH (absolute path to ../suppliersync/suppliersync.db)
   # - ORCHESTRATOR_API_URL (defaults to http://localhost:8000)
   ```

## Run
```bash
npm i
npm run dev  # http://localhost:3000
```

Click **Run Orchestration** in the dashboard to trigger an orchestration via the FastAPI service.
