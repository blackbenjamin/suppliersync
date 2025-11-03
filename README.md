# SupplierSync — Multi-Agent AI Orchestrator for E-Commerce

> **A production-ready demonstration of an agentic AI system for supplier management, dynamic pricing, and customer experience optimization — inspired by Wayfair's operational challenges.**

[![Live Demo](https://img.shields.io/badge/Live%20Demo-projects.benjaminblack.consulting-blue)](https://projects.benjaminblack.consulting)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black)](https://github.com/YOUR_USERNAME/suppliersync)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Product Vision

SupplierSync addresses the core challenge in modern e-commerce: **managing complex supplier relationships, optimizing pricing in real-time, and delivering exceptional customer experiences** — all while maintaining profitability and compliance.

This system demonstrates how **multi-agent AI orchestration** can automate critical business processes that traditionally require significant human oversight, enabling:
- **Automated supplier data synchronization** (SKUs, availability, wholesale pricing)
- **Intelligent price optimization** with governance and compliance
- **Proactive customer experience management** based on real-time signals
- **Full observability** into AI decision-making and costs

## 🏗️ Architecture Overview

SupplierSync is built as a **decoupled, production-ready system** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Dashboard                         │
│  (Real-time monitoring, metrics, governance decisions)      │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│              FastAPI Orchestration Service                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Supplier   │  │    Buyer/    │  │     CX      │     │
│  │    Agent     │  │   Pricing    │  │    Agent    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│           │              │              │                   │
│           └──────────────┴──────────────┘                  │
│                      │                                      │
│              Orchestrator (Transaction Manager)            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              SQLite Database (WAL Mode)                     │
│  (Products, Price Events, Governance Decisions, Metrics)   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              RAG Vectorstore (ChromaDB)                      │
│  (Supplier documents, pricing policies, category specs)    │
└─────────────────────────────────────────────────────────────┘
```

### Key Architectural Decisions

1. **Multi-Agent Orchestration**: Each agent (Supplier, Buyer, CX) has a focused responsibility, enabling independent testing and scaling
2. **Transaction-Based Workflow**: All agent operations run within a single database transaction for data consistency
3. **Governance as Code**: Pricing rules are configurable via environment variables, enabling A/B testing and rapid policy changes
4. **Observability First**: Every agent call is logged with tokens, latency, and cost — enabling cost optimization and debugging
5. **RAG Integration**: Optional vectorstore for context-aware agent decisions based on supplier documentation

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** (for orchestration service)
- **Node.js 20+** (for dashboard)
- **OpenAI API Key** (for LLM-powered agents)
- **Docker & Docker Compose** (optional, for containerized deployment)

### Option 1: Docker Compose (Recommended)

**From the project root:**

```bash
# 1. Set your OpenAI API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 2. Start both services
docker-compose up --build -d

# 3. Initialize the database with sample data
docker-compose exec api python populate_inventory.py

# 4. Access the dashboard
open http://localhost:3001
```

**Services:**
- **Dashboard**: http://localhost:3001
- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

### Option 2: Local Development

**1. Python Service:**
```bash
cd suppliersync
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
# Edit .env: Set OPENAI_API_KEY and SQLITE_PATH
uvicorn api:app --reload --port 8000
```

**2. Next.js Dashboard:**
```bash
cd dashboard
npm install
cp env.local.example .env.local
# Edit .env.local: Set SQLITE_PATH (same as Python service)
npm run dev
```

**3. Initialize Database:**
```bash
cd suppliersync
source .venv/bin/activate
python populate_inventory.py  # Populates with 20 Wayfair-style products
```

## 📊 Features

### 🤖 Multi-Agent System

**Supplier Agent**
- Monitors supplier data updates (SKUs, availability, wholesale prices)
- Proposes catalog changes based on market conditions
- Maintains supplier relationships and compliance

**Buyer/Pricing Agent**
- Optimizes retail prices based on market signals and profit goals
- Proposes price changes with business justification
- Respects governance rules (margins, price drift limits, MAP policies)

**CX Agent**
- Analyzes customer events (views, cart additions, purchases, returns)
- Identifies products needing attention (high return rates, low conversion)
- Proposes CX improvements (product descriptions, pricing adjustments)

**Orchestrator**
- Coordinates agent execution within transactions
- Enforces governance policies before applying changes
- Tracks metrics, costs, and decision rationale
- Generates run IDs for traceability

### 🛡️ Governance & Compliance

**Configurable Rules** (via environment variables):
- `MIN_MARGIN_PCT`: Minimum profit margin (default: 5%)
- `MAX_DAILY_PRICE_DRIFT`: Maximum price change per day (default: 20%)
- `BLOCKED_CATEGORIES`: Categories where price changes are blocked
- `ALLOWED_CATEGORIES`: Whitelist of categories for price changes
- `MAP_POLICY`: Minimum Advertised Price enforcement (framework ready)

**Governance Decisions**:
- All price changes are evaluated against rules
- Rejected changes are logged with detailed reasons
- Dashboard shows governance decision history

### 📈 Observability & Metrics

**Real-time Metrics Dashboard**:
- Total products, price events, rejected prices, CX events
- Agent performance (tokens, latency, cost per run)
- Cost tracking (total spend, average cost per orchestration)
- Recent orchestration runs with run IDs

**Agent Telemetry**:
- Every LLM call is logged with:
  - Input/output tokens
  - Latency
  - Cost estimate
  - Model used

### 🔍 RAG (Retrieval Augmented Generation)

**Vectorstore Integration**:
- Stores supplier documentation (pricing policies, category specs, onboarding guides)
- Enables context-aware agent decisions
- Status dashboard shows document count and chunk information
- Rebuild capability for adding new documents

**Usage**:
- Documents in `suppliersync/data/docs/` are automatically indexed
- Agents can query vectorstore for relevant context
- Supports PDF and text files

## 📡 API Reference

### Core Endpoints

#### `POST /orchestrate`
Run one orchestration step (all agents execute in sequence).

**Response:**
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "supplier_updates": [...],
  "approved_prices": [...],
  "rejected_prices": [...],
  "cx_actions": [...]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/orchestrate
```

#### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "db_path": "suppliersync.db"
}
```

### RAG Endpoints

#### `GET /rag/status`
Check RAG vectorstore status.

**Response:**
```json
{
  "has_docs_directory": true,
  "has_vectorstore": true,
  "docs_path": "data/docs",
  "persist_path": ".chroma",
  "document_count": 22,
  "file_count": 3,
  "status": "ready"
}
```

#### `POST /rag/rebuild`
Rebuild the RAG vectorstore from documents.

**Response:**
```json
{
  "status": "success",
  "message": "Vectorstore rebuilt successfully. 3 files split into 22 chunks.",
  "file_count": 3,
  "chunk_count": 22
}
```

## 🧪 Testing

### Python Tests
```bash
cd suppliersync
source .venv/bin/activate
pip install -r requirements-test.txt
pytest tests/
```

### Dashboard Tests (Playwright)
```bash
cd dashboard
npm install -D @playwright/test
npx playwright install
npx playwright test
```

### Integration Test
```bash
./test_integration.sh
```

## 📁 Project Structure

```
suppliersync_demo/
├── suppliersync/              # Python FastAPI service
│   ├── agents/                # Agent implementations
│   │   ├── supplier_agent.py # Supplier data updates
│   │   ├── buyer_agent.py     # Price optimization
│   │   ├── cx_agent.py        # Customer experience
│   │   └── orchestrator.py    # Coordination & transaction mgmt
│   ├── core/                  # Core functionality
│   │   ├── llm.py             # LLM client & utilities
│   │   ├── governance.py     # Pricing rules & enforcement
│   │   ├── rag.py             # Vectorstore management
│   │   ├── types.py           # Pydantic models
│   │   └── prompts.py         # Agent prompts
│   ├── data/                  # Seed data & documents
│   │   ├── docs/              # RAG documents
│   │   ├── seed_products.csv  # Sample products
│   │   └── seed_suppliers.csv # Sample suppliers
│   ├── db/                    # Database schema
│   │   └── schema.sql
│   ├── tests/                 # Pytest tests
│   ├── api.py                 # FastAPI application
│   ├── main.py                # Direct execution entry point
│   ├── populate_inventory.py  # Database initialization
│   └── Dockerfile
│
├── dashboard/                 # Next.js dashboard
│   ├── app/                   # Next.js app router
│   │   ├── (api)/            # API routes (proxies)
│   │   └── page.tsx          # Main dashboard
│   ├── components/           # React components
│   │   ├── StatsCards.tsx    # Metrics overview
│   │   ├── MetricsView.tsx   # Agent telemetry
│   │   ├── GovernanceTable.tsx # Rejected prices
│   │   ├── RAGStatus.tsx     # Vectorstore status
│   │   └── ...
│   ├── lib/                  # Utilities
│   │   ├── db.ts             # Database client
│   │   └── dateUtils.ts      # Date formatting
│   └── Dockerfile
│
├── docker-compose.yml         # Container orchestration
├── README.md                  # This file
└── test_integration.sh        # Integration test script
```

## ⚙️ Configuration

### Environment Variables

**Python Service** (`suppliersync/.env`):
```bash
OPENAI_API_KEY=sk-...              # Required: OpenAI API key
OPENAI_MODEL=gpt-4o-mini           # Model to use (default: gpt-4o-mini)
OPENAI_TIMEOUT=30                  # Request timeout in seconds
OPENAI_MAX_RETRIES=3               # Retry attempts
SQLITE_PATH=suppliersync.db         # Database path
API_PORT=8000                      # FastAPI port
MIN_MARGIN_PCT=5                   # Minimum profit margin %
MAX_DAILY_PRICE_DRIFT=20           # Max daily price change %
BLOCKED_CATEGORIES=                 # Comma-separated blocked categories
ALLOWED_CATEGORIES=                 # Comma-separated allowed categories
RAG_DOCS_PATH=data/docs             # RAG documents directory
RAG_PERSIST_PATH=.chroma            # Vectorstore persistence path
```

**Dashboard** (`dashboard/.env.local`):
```bash
SQLITE_PATH=/absolute/path/to/suppliersync.db  # Must match Python service
ORCHESTRATOR_API_URL=http://localhost:8000     # FastAPI service URL
```

## 🎯 Business Value

**For Product Managers:**
- Demonstrates how to structure multi-agent systems for complex business workflows
- Shows governance-as-code approach for rapid policy iteration
- Provides full observability into AI decision-making and costs
- Enables A/B testing of pricing strategies and agent behaviors

**For Engineering Teams:**
- Production-ready architecture with proper error handling and transactions
- Clear separation of concerns (agents, orchestration, governance)
- Comprehensive logging and telemetry for debugging
- Docker-based deployment for consistent environments

**For Business Stakeholders:**
- Automated supplier management reduces manual effort
- Dynamic pricing optimization increases profitability
- Customer experience improvements drive conversion
- Full audit trail for compliance and decision review

## 🔒 Security

**Security Features:**
- ✅ Input validation with Pydantic models
- ✅ Rate limiting (endpoint-specific limits)
- ✅ Structured logging with error sanitization
- ✅ Path validation to prevent traversal attacks
- ✅ CORS hardening (specific methods and headers)
- ✅ SQL injection prevention (whitelist validation)
- ✅ Database backup utilities
- ✅ Dependency scanning scripts

**Security Documentation:**
- [SECURITY.md](SECURITY.md) - Complete security review and recommendations
- [DATABASE_SECURITY.md](DATABASE_SECURITY.md) - Database security best practices
- [DEPENDENCY_SECURITY.md](DEPENDENCY_SECURITY.md) - Dependency security guide

**For Production:**
- ⚠️ Authentication/authorization required
- ⚠️ Database encryption at rest (SQLCipher or volume encryption)
- ⚠️ Secrets management service (AWS Secrets Manager, HashiCorp Vault)
- ⚠️ Automated dependency scanning in CI/CD

## 🧪 Testing

**Test Suite:**
- ✅ Comprehensive test suite (`test_all.sh`)
- ✅ Python unit tests (pytest)
- ✅ Integration tests (`test_integration.sh`)
- ✅ Security tests (path validation, SQL injection prevention)
- ✅ Database tests (backup, integrity, operations)
- ✅ API tests (endpoints, error handling, security)

**Test Coverage:**
- Governance rules (8 tests)
- Security features (14 tests)
- Database operations (5 tests)
- API endpoints (6 tests)

**Running Tests:**
```bash
# Run all tests
./test_all.sh

# Run Python unit tests
cd suppliersync && pytest tests/ -v

# Run integration tests
./test_integration.sh
```

See [TESTING.md](TESTING.md) for detailed testing documentation.

## 🚀 Deployment

**Live Demo**: [projects.benjaminblack.consulting](https://projects.benjaminblack.consulting)

This project is deployed on:
- **Dashboard**: Vercel (Next.js)
- **API**: Railway (FastAPI)
- **DNS**: Cloudflare

**Quick Start**: See [QUICK_START.md](QUICK_START.md) for deployment instructions.
**Full Guide**: See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment documentation.

## 🔮 Future Enhancements

**Potential Improvements:**
- [ ] Real-time updates via WebSockets or Server-Sent Events
- [ ] Advanced pricing strategies (demand forecasting, competitor analysis)
- [ ] Multi-tenant support for multiple suppliers/brands
- [ ] GraphQL API for more flexible data querying
- [ ] Automated testing with synthetic data generation
- [ ] Cost optimization recommendations based on telemetry
- [ ] Integration with external data sources (competitor prices, market trends)
- [ ] Advanced RAG with multi-modal support (images, PDFs)

## 📝 License

MIT License — See LICENSE file for details.

## 🙏 Acknowledgments

Inspired by Wayfair's operational challenges in supplier management, dynamic pricing, and customer experience optimization. This system demonstrates how agentic AI can automate and optimize complex business processes.

---

**Built with:**
- FastAPI (Python backend)
- Next.js 14 (React dashboard)
- OpenAI GPT-4 (LLM agents)
- SQLite (database)
- ChromaDB (vectorstore)
- Docker (containerization)
