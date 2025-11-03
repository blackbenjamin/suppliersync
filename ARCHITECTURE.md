# Architecture Documentation

This document describes the architecture, design decisions, and patterns used in SupplierSync.

## System Overview

SupplierSync is a multi-agent AI orchestration system designed for e-commerce supplier management, dynamic pricing, and customer experience optimization. The system follows a **service-oriented architecture** with clear separation between the orchestration backend and the monitoring dashboard.

## Design Principles

1. **Agent Autonomy**: Each agent (Supplier, Buyer, CX) operates independently with a focused responsibility
2. **Transaction Safety**: All operations run within database transactions for data consistency
3. **Governance as Code**: Business rules are configurable via environment variables
4. **Observability First**: Every agent action is logged with telemetry for cost tracking and debugging
5. **Fail-Safe Defaults**: System gracefully handles errors and continues operating

## Component Architecture

### Backend Service (FastAPI)

**Location**: `suppliersync/`

**Responsibilities**:
- Agent orchestration and coordination
- Transaction management
- Governance rule enforcement
- Database operations
- RAG vectorstore management

**Key Components**:

#### Orchestrator (`agents/orchestrator.py`)
- **Purpose**: Coordinates agent execution and manages transactions
- **Pattern**: Transaction Script Pattern
- **Key Methods**:
  - `step()`: Executes one orchestration cycle
  - `_fetch_catalog()`: Retrieves active product catalog
  - `_fetch_price_history()`: Gets price history for governance checks
  - `_apply_changes()`: Applies approved changes within transaction

#### Agents
Each agent follows a consistent pattern:
1. **Input**: Context (catalog, events, history)
2. **Processing**: LLM call with structured output
3. **Output**: Pydantic-validated results with telemetry

**Supplier Agent** (`agents/supplier_agent.py`):
- Monitors supplier data changes
- Proposes catalog updates (new SKUs, price changes, availability)

**Buyer Agent** (`agents/buyer_agent.py`):
- Optimizes retail pricing
- Proposes price changes with business justification
- Considers market conditions and profit goals

**CX Agent** (`agents/cx_agent.py`):
- Analyzes customer events (views, carts, purchases, returns)
- Identifies products needing attention
- Proposes customer experience improvements

#### Governance (`core/governance.py`)
- **Purpose**: Enforce business rules on price changes
- **Pattern**: Policy Pattern
- **Rules**:
  1. Retail price ≥ wholesale price
  2. Margin ≥ MIN_MARGIN_PCT (default 5%)
  3. Daily price change ≤ MAX_DAILY_PRICE_DRIFT (default 20%)
  4. Category allow/block list checks
  5. MAP (Minimum Advertised Price) enforcement

#### LLM Client (`core/llm.py`)
- **Purpose**: Centralized LLM interaction with error handling
- **Features**:
  - Lazy initialization (no startup dependency on API key)
  - Configurable timeouts and retries
  - Structured JSON output parsing
  - Token counting and cost estimation

#### RAG (`core/rag.py`)
- **Purpose**: Vectorstore management for document retrieval
- **Technology**: ChromaDB with SentenceTransformer embeddings
- **Features**:
  - Document chunking (800 chars, 120 overlap)
  - Collection management (auto-clear on rebuild)
  - File and chunk count tracking

### Frontend Dashboard (Next.js)

**Location**: `dashboard/`

**Responsibilities**:
- Real-time monitoring and visualization
- User interaction (orchestration triggers, RAG rebuilds)
- Metrics and observability display

**Key Components**:

#### Server-Side Rendering
- **Pattern**: Server Components for data fetching
- **Benefits**: Direct database access, no API calls needed
- **Caching**: Explicitly disabled for real-time data

#### API Routes (`app/(api)/`)
- **Purpose**: Proxy endpoints to Python service
- **Endpoints**:
  - `/orchestrate`: Triggers orchestration
  - `/rag-status`: Checks RAG vectorstore status
  - `/rag-rebuild`: Rebuilds vectorstore

#### Components
- **StatsCards**: Overview metrics (products, events, rejected prices)
- **MetricsView**: Agent telemetry and cost tracking
- **GovernanceTable**: Rejected price changes with reasons
- **RAGStatus**: Vectorstore status and rebuild controls

### Database (SQLite)

**Location**: `suppliersync/suppliersync.db` (or configured path)

**Schema**: See `db/schema.sql`

**Key Features**:
- **WAL Mode**: Enables concurrent reads/writes
- **Indexes**: Optimized for common queries (SKU lookups, time-based queries)
- **Run IDs**: Every event is tagged with a `run_id` for traceability

**Tables**:
- `products`: Catalog of products
- `suppliers`: Supplier information
- `price_events`: Approved price changes
- `rejected_prices`: Rejected price changes with reasons
- `supplier_updates`: Supplier data changes
- `cx_events`: Customer experience events
- `agent_logs`: Agent telemetry (tokens, latency, cost)

## Data Flow

### Orchestration Cycle

```
1. User triggers orchestration (via dashboard or API)
   ↓
2. Orchestrator.step() executes:
   a. Fetch catalog and context
   b. Supplier Agent proposes updates
   c. Buyer Agent proposes price changes
   d. Governance enforces rules on price changes
   e. CX Agent proposes actions
   ↓
3. All changes applied within transaction:
   - Supplier updates → products table
   - Approved prices → price_events table
   - Rejected prices → rejected_prices table
   - CX actions → cx_events table
   - Agent telemetry → agent_logs table
   ↓
4. Transaction commits
   ↓
5. Dashboard refreshes to show new data
```

### RAG Integration Flow

```
1. Documents added to data/docs/
   ↓
2. User triggers rebuild (via dashboard)
   ↓
3. build_vectorstore() executes:
   a. Clear existing collection
   b. Load documents from directory
   c. Split into chunks (800 chars, 120 overlap)
   d. Create embeddings (SentenceTransformer)
   e. Store in ChromaDB
   ↓
4. Agents can query vectorstore for context
   (Framework ready, not yet implemented in agents)
```

## Design Patterns

### Transaction Script
- **Use**: Orchestrator coordinates all operations within a single transaction
- **Benefit**: Ensures data consistency and atomicity

### Agent Pattern
- **Use**: Each agent is a focused, autonomous component
- **Benefit**: Easy to test, modify, and scale independently

### Policy Pattern
- **Use**: Governance rules are separate from agent logic
- **Benefit**: Business rules can change without modifying agent code

### Repository Pattern (implicit)
- **Use**: Database operations are centralized in Orchestrator
- **Benefit**: Single source of truth for data access

## Error Handling

### LLM Calls
- **Timeout**: Configurable timeout (default 30s)
- **Retries**: Configurable retries (default 3)
- **Fallback**: Returns empty results on failure (doesn't crash system)

### Database Operations
- **Transactions**: Wrapped in try/except with rollback
- **Schema Migration**: Automatic schema updates on startup
- **Indexes**: Created automatically if missing

### API Calls
- **Health Checks**: Available at `/health`
- **Error Responses**: Structured error messages with status codes
- **Timeout Handling**: 120s timeout for orchestration (long-running operation)

## Scalability Considerations

### Current Limitations
- **SQLite**: Single-file database (not distributed)
- **Synchronous Agents**: Agents run sequentially (not parallel)
- **Single Process**: FastAPI runs in single process (not multi-worker)

### Future Scalability Options
- **Database**: Migrate to PostgreSQL for multi-instance support
- **Agent Parallelization**: Run agents concurrently (with dependency resolution)
- **Worker Pool**: Use FastAPI with multiple workers or async tasks
- **Caching**: Add Redis for frequently accessed data
- **Message Queue**: Use Celery/RQ for async agent execution

## Security Considerations

### Current Implementation
- **API Keys**: Stored in environment variables (not hardcoded)
- **CORS**: Restricted to localhost (development only)
- **SQL Injection**: Protected by parameterized queries

### Production Readiness
- **Authentication**: Add API key or JWT authentication
- **Authorization**: Add role-based access control
- **Rate Limiting**: Add rate limiting for API endpoints
- **Input Validation**: Enhanced Pydantic validation
- **Secrets Management**: Use secret management service (AWS Secrets Manager, etc.)

## Testing Strategy

### Unit Tests
- **Location**: `suppliersync/tests/`
- **Coverage**: Governance rules, agent validation
- **Framework**: Pytest

### Integration Tests
- **Location**: `test_integration.sh`
- **Coverage**: API endpoints, database operations
- **Framework**: Shell scripts with curl

### E2E Tests
- **Location**: `dashboard/tests/`
- **Coverage**: Dashboard UI, orchestration flow
- **Framework**: Playwright

## Deployment

### Docker Compose
- **Purpose**: Local development and demonstration
- **Services**: API service, Dashboard service
- **Volumes**: Shared database file

### Production Deployment Options
1. **Container Orchestration**: Kubernetes, ECS, or similar
2. **Managed Services**: 
   - API: AWS Lambda, Google Cloud Run
   - Dashboard: Vercel, Netlify
   - Database: AWS RDS, Google Cloud SQL
3. **CI/CD**: GitHub Actions, GitLab CI, or similar

## Monitoring & Observability

### Metrics Collected
- **Agent Performance**: Tokens, latency, cost per call
- **Business Metrics**: Price changes, rejections, CX events
- **System Health**: Database connectivity, API availability

### Logging
- **Agent Logs**: Stored in `agent_logs` table
- **Application Logs**: FastAPI/Uvicorn logs
- **Error Logs**: Structured error messages

### Dashboard Features
- **Real-time Metrics**: Stats cards update on page load
- **Cost Tracking**: Total spend and per-run costs
- **Decision History**: All price changes and rejections

## Future Enhancements

See README.md for potential improvements and roadmap.

