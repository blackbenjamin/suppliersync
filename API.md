# API Documentation

Complete API reference for the SupplierSync Orchestrator service.

## Base URL

**Local Development**: `http://localhost:8000`  
**Docker**: `http://localhost:8000`

## Endpoints

### Health Check

#### `GET /health`

Check if the service is running and healthy.

**Response:**
```json
{
  "status": "ok",
  "db_path": "suppliersync.db"
}
```

**Example:**
```bash
curl http://localhost:8000/health
```

---

### Orchestration

#### `POST /orchestrate`

Run one orchestration cycle. This triggers all agents (Supplier, Buyer, CX) to execute in sequence and applies all changes within a single database transaction.

**Request Body:** None (empty POST)

**Response:**
```json
{
  "run_id": "550e8400-e29b-41d4-a716-446655440000",
  "supplier_updates": [
    {
      "sku": "WF-001",
      "field": "wholesale_price",
      "new_value": 95.0,
      "reason": "supplier_price_update"
    }
  ],
  "approved_prices": [
    {
      "sku": "WF-001",
      "new_price": 149.99,
      "reason": "market_optimization"
    }
  ],
  "rejected_prices": [
    {
      "sku": "WF-002",
      "new_price": 89.99,
      "reject_reason": "margin_too_low",
      "reject_details": "Proposed price $89.99 results in margin of 3.2%, below minimum of 5.0%"
    }
  ],
  "cx_actions": [
    {
      "sku": "WF-003",
      "action": "update_description",
      "reason": "high_return_rate",
      "details": "Product has 15% return rate, suggesting description may be misleading"
    }
  ]
}
```

**Response Fields:**
- `run_id`: Unique identifier for this orchestration run (for traceability)
- `supplier_updates`: List of supplier data changes applied (SKUs, availability, wholesale prices)
- `approved_prices`: List of price changes that passed governance checks
- `rejected_prices`: List of price changes that failed governance (with reasons)
- `cx_actions`: List of customer experience actions proposed

**Status Codes:**
- `200 OK`: Orchestration completed successfully
- `500 Internal Server Error`: Error during orchestration

**Example:**
```bash
curl -X POST http://localhost:8000/orchestrate
```

**Timeout:**
- Default: 120 seconds (orchestration can take a while with multiple LLM calls)

---

### RAG (Retrieval Augmented Generation)

#### `GET /rag/status`

Check the status of the RAG vectorstore.

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

**Response Fields:**
- `has_docs_directory`: Whether the documents directory exists
- `has_vectorstore`: Whether the vectorstore has been created
- `docs_path`: Path to documents directory
- `persist_path`: Path to vectorstore persistence directory
- `document_count`: Number of chunks in vectorstore (documents are split into chunks)
- `file_count`: Number of original files in documents directory
- `status`: "ready" if vectorstore exists and has documents, "not_ready" otherwise

**Example:**
```bash
curl http://localhost:8000/rag/status
```

---

#### `POST /rag/rebuild`

Rebuild the RAG vectorstore from documents in the documents directory. This will:
1. Clear the existing vectorstore (if it exists)
2. Load all documents from `data/docs/`
3. Split documents into chunks (800 characters, 120 character overlap)
4. Create embeddings and store in ChromaDB

**Request Body:** None (empty POST)

**Response:**
```json
{
  "status": "success",
  "message": "Vectorstore rebuilt successfully. 3 files split into 22 chunks.",
  "docs_path": "data/docs",
  "persist_path": ".chroma",
  "document_count": 22,
  "file_count": 3,
  "chunk_count": 22
}
```

**Response Fields:**
- `status`: "success" or "error"
- `message`: Human-readable status message
- `docs_path`: Path to documents directory
- `persist_path`: Path to vectorstore persistence directory
- `document_count`: Number of chunks in vectorstore
- `file_count`: Number of original files processed
- `chunk_count`: Number of chunks created (same as document_count)

**Status Codes:**
- `200 OK`: Vectorstore rebuilt successfully
- `500 Internal Server Error`: Error during rebuild

**Example:**
```bash
curl -X POST http://localhost:8000/rag/rebuild
```

**Note:**
- Documents are automatically split into chunks (800 chars, 120 overlap)
- Supports `.txt` and `.pdf` files
- Rebuild clears existing vectorstore to prevent duplicates

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Status Codes:**
- `400 Bad Request`: Invalid request
- `404 Not Found`: Endpoint not found
- `500 Internal Server Error`: Server error
- `504 Gateway Timeout`: Request timed out (orchestration)

---

## CORS

The API allows CORS requests from:
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://localhost:3001`
- `http://127.0.0.1:3001`

This enables the Next.js dashboard to make API calls from the browser.

---

## Rate Limiting

Currently, there is no rate limiting. For production deployments, consider adding rate limiting to prevent abuse.

---

## Authentication

Currently, there is no authentication. For production deployments, add:
- API key authentication
- JWT tokens
- OAuth2
- Role-based access control

---

## Examples

### Complete Orchestration Flow

```bash
# 1. Check health
curl http://localhost:8000/health

# 2. Run orchestration
curl -X POST http://localhost:8000/orchestrate

# 3. Check RAG status
curl http://localhost:8000/rag/status

# 4. Rebuild vectorstore (if needed)
curl -X POST http://localhost:8000/rag/rebuild
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# Run orchestration
response = requests.post(f"{BASE_URL}/orchestrate", timeout=120)
result = response.json()
print(f"Run ID: {result['run_id']}")
print(f"Approved prices: {len(result['approved_prices'])}")
print(f"Rejected prices: {len(result['rejected_prices'])}")

# Check RAG status
response = requests.get(f"{BASE_URL}/rag/status")
status = response.json()
print(f"RAG status: {status['status']}")
print(f"Documents: {status['file_count']} files, {status['document_count']} chunks")
```

---

## Next Steps

For more information, see:
- [README.md](README.md) - Project overview and setup
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design decisions

