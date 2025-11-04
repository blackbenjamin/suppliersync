"""
FastAPI service for SupplierSync orchestration.
Run with: uvicorn api:app --reload --port 8000
"""

import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from agents.orchestrator import Orchestrator
from core.security import validate_path

# RAG is optional - only import if available
try:
    from core.rag import build_vectorstore
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    logger.warning("RAG dependencies not installed. RAG endpoints will be disabled.")

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
    datefmt='%Y-%m-%dT%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Try to import slowapi for rate limiting
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False
    logger.warning("slowapi not installed, rate limiting disabled")

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="SupplierSync Orchestrator API")

# Rate limiting (if slowapi is available)
if SLOWAPI_AVAILABLE:
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
else:
    # Dummy limiter decorator if slowapi is not available
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
    limiter = DummyLimiter()

# Trusted Host middleware (for production)
# In production, set TRUSTED_HOSTS env var with allowed hosts
trusted_hosts = os.getenv("TRUSTED_HOSTS", "*").split(",")
if trusted_hosts != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

# Allow CORS for dashboard
# Security: In production, restrict origins, methods, and headers
# For development, allow localhost origins only
allowed_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Restrict to specific methods (not "*")
    allow_headers=["Content-Type", "Authorization"],  # Restrict to specific headers (not "*")
)

DB_PATH = os.getenv("SQLITE_PATH", "suppliersync.db")

# Request size limit (10MB default)
MAX_REQUEST_SIZE = int(os.getenv("MAX_REQUEST_SIZE", 10 * 1024 * 1024))  # 10MB


# Input validation models
class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(default="ok", description="Service status")


class RAGRebuildRequest(BaseModel):
    """RAG rebuild request model (currently no parameters, but validates request structure)."""
    pass


class RAGRebuildResponse(BaseModel):
    """RAG rebuild response model."""
    status: str = Field(description="Operation status: success or error")
    message: str = Field(description="Human-readable message")
    docs_path: str = Field(description="Path to documents directory")
    persist_path: str = Field(description="Path to vectorstore persistence directory")
    document_count: int = Field(ge=0, description="Number of chunks in vectorstore")
    file_count: int = Field(ge=0, description="Number of original files")
    chunk_count: int = Field(ge=0, description="Number of chunks created")


class RAGStatusResponse(BaseModel):
    """RAG status response model."""
    has_docs_directory: bool = Field(description="Whether documents directory exists")
    has_vectorstore: bool = Field(description="Whether vectorstore exists")
    docs_path: str = Field(description="Path to documents directory")
    persist_path: str = Field(description="Path to vectorstore persistence directory")
    document_count: int = Field(ge=0, description="Number of chunks in vectorstore")
    file_count: int = Field(ge=0, description="Number of original files")
    status: str = Field(description="Status: ready, not_ready, or error")


class OrchestrateResponse(BaseModel):
    """Orchestration response model."""
    run_id: str = Field(description="Unique identifier for this orchestration run")
    supplier_updates: list = Field(default_factory=list, description="Supplier data changes applied")
    approved_prices: list = Field(default_factory=list, description="Price changes that passed governance")
    rejected_prices: list = Field(default_factory=list, description="Price changes that failed governance")
    cx_actions: list = Field(default_factory=list, description="Customer experience actions proposed")


# Request size limit middleware
@app.middleware("http")
async def check_request_size(request: Request, call_next):
    """Check request size to prevent DoS attacks."""
    if request.method in ["POST", "PUT", "PATCH"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_REQUEST_SIZE:
            logger.warning(f"Request size exceeded: {content_length} bytes")
            raise HTTPException(status_code=413, detail="Request too large")
    response = await call_next(request)
    return response


@app.get("/health", response_model=HealthResponse)
@limiter.limit("100/minute")  # Rate limit: 100 requests per minute
async def health(request: Request):
    """
    Health check endpoint.
    
    Note: Does not expose internal paths for security.
    """
    logger.info("Health check requested")
    return {"status": "ok"}


@app.post("/rag/rebuild", response_model=RAGRebuildResponse)
@limiter.limit("5/minute")  # Rate limit: 5 rebuilds per minute (expensive operation)
async def rebuild_rag(request: Request):
    """
    Rebuild the RAG vectorstore from documents in data/docs.
    Returns status and document count.
    
    Security: Validates paths and rate-limited to prevent abuse.
    """
    if not RAG_AVAILABLE:
        raise HTTPException(status_code=503, detail="RAG functionality not available. Install langchain, chromadb, and sentence-transformers to enable.")
    logger.info("RAG rebuild requested")
    try:
        # Validate and sanitize paths
        docs_path = os.getenv("RAG_DOCS_PATH", "data/docs")
        persist_path = os.getenv("RAG_PERSIST_PATH", ".chroma")
        
        # Use security utilities for path validation
        try:
            # Get base directory for validation (current working directory)
            base_dir = os.getcwd()
            docs_path = validate_path(docs_path, base_dir=base_dir, allow_absolute=False)
            persist_path = validate_path(persist_path, base_dir=base_dir, allow_absolute=False)
        except ValueError as e:
            logger.error(f"Invalid path in RAG rebuild: {e}")
            raise HTTPException(status_code=400, detail="Invalid path configuration")
        
        if not os.path.isdir(docs_path):
            logger.warning(f"Documents directory not found: {docs_path}")
            return JSONResponse({
                "status": "error",
                "message": f"Documents directory not found: {docs_path}",
                "docs_path": docs_path,
                "persist_path": persist_path,
                "document_count": 0,
                "file_count": 0,
                "chunk_count": 0,
            })
        
        result = build_vectorstore(path=docs_path, persist=persist_path, clear_existing=True)
        if result is None:
            logger.error("Failed to build vectorstore")
            return JSONResponse({
                "status": "error",
                "message": "Failed to build vectorstore",
                "docs_path": docs_path,
                "persist_path": persist_path,
                "document_count": 0,
                "file_count": 0,
                "chunk_count": 0,
            })
        
        vs, file_count, chunk_count = result
        logger.info(f"RAG vectorstore rebuilt: {file_count} files, {chunk_count} chunks")
        
        return JSONResponse({
            "status": "success",
            "message": f"Vectorstore rebuilt successfully. {file_count} files split into {chunk_count} chunks.",
            "docs_path": docs_path,
            "persist_path": persist_path,
            "document_count": chunk_count,  # Total chunks in vectorstore
            "file_count": file_count,  # Original number of files
            "chunk_count": chunk_count,  # Number of chunks created
        })
    except HTTPException:
        raise
    except Exception as e:
        # Log detailed error server-side (for debugging)
        logger.error(f"RAG rebuild error: {e}", exc_info=True)
        # Return generic error message to client (no information leakage)
        raise HTTPException(status_code=500, detail="Failed to rebuild vectorstore. Check server logs for details.")


@app.get("/rag/status", response_model=RAGStatusResponse)
@limiter.limit("30/minute")  # Rate limit: 30 requests per minute
async def rag_status(request: Request):
    """Check RAG vectorstore status."""
    if not RAG_AVAILABLE:
        return JSONResponse({
            "status": "not_ready",
            "has_docs_directory": False,
            "has_vectorstore": False,
            "docs_path": os.getenv("RAG_DOCS_PATH", "data/docs"),
            "persist_path": os.getenv("RAG_PERSIST_PATH", ".chroma"),
            "document_count": 0,
            "file_count": 0,
            "message": "RAG dependencies not installed"
        })
    try:
        persist_path = os.getenv("RAG_PERSIST_PATH", ".chroma")
        docs_path = os.getenv("RAG_DOCS_PATH", "data/docs")
        
        # Validate paths
        try:
            base_dir = os.getcwd()
            docs_path = validate_path(docs_path, base_dir=base_dir, allow_absolute=False)
            persist_path = validate_path(persist_path, base_dir=base_dir, allow_absolute=False)
        except ValueError as e:
            logger.error(f"Invalid path in RAG status: {e}")
            return JSONResponse({
                "status": "error",
                "has_docs_directory": False,
                "has_vectorstore": False,
                "docs_path": docs_path,
                "persist_path": persist_path,
                "document_count": 0,
                "file_count": 0,
                "status": "error",
            })
        
        has_docs_dir = os.path.isdir(docs_path)
        has_vectorstore = os.path.exists(persist_path)
        
        count = 0
        if has_vectorstore:
            try:
                from langchain_community.embeddings import SentenceTransformerEmbeddings
                from langchain_community.vectorstores import Chroma
                EMB = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
                # Try to get count from all collections (in case of multiple)
                import chromadb
                client = chromadb.PersistentClient(path=persist_path)
                collections = client.list_collections()
                count = 0
                for col in collections:
                    count += col.count()
                # Fallback to langchain collection if no collections found
                if count == 0:
                    vs = Chroma(persist_directory=persist_path, embedding_function=EMB)
                    collection = vs._collection
                    count = collection.count() if hasattr(collection, 'count') else 0
            except Exception as e:
                logger.warning(f"Error counting vectorstore documents: {e}")
                pass
        
        # Try to get file count from docs directory
        file_count = 0
        if has_docs_dir:
            try:
                file_count = len([f for f in os.listdir(docs_path) if os.path.isfile(os.path.join(docs_path, f))])
            except Exception as e:
                logger.warning(f"Error counting files in {docs_path}: {e}")
                pass
        
        return JSONResponse({
            "has_docs_directory": has_docs_dir,
            "has_vectorstore": has_vectorstore,
            "docs_path": docs_path,
            "persist_path": persist_path,
            "document_count": count,  # Chunk count
            "file_count": file_count,  # Original file count
            "status": "ready" if (has_vectorstore and count > 0) else "not_ready",
        })
    except Exception as e:
        # Log detailed error server-side (for debugging)
        logger.error(f"RAG status error: {e}", exc_info=True)
        # Return generic error message to client (no information leakage)
        return JSONResponse({
            "status": "error",
            "has_docs_directory": False,
            "has_vectorstore": False,
            "docs_path": "",
            "persist_path": "",
            "document_count": 0,
            "file_count": 0,
            "status": "error",
        })


@app.post("/orchestrate", response_model=OrchestrateResponse)
@limiter.limit("10/minute")  # Rate limit: 10 orchestration runs per minute (expensive operation)
async def orchestrate(request: Request):
    """
    Run one orchestration step.
    Returns the run_id and all agent outputs.
    
    Security: Rate-limited to prevent abuse and cost escalation.
    """
    logger.info("Orchestration requested")
    try:
        orch = Orchestrator(DB_PATH)
        result = orch.step()
        logger.info(f"Orchestration completed: run_id={result.get('run_id')}, "
                   f"approved={len(result.get('approved_prices', []))}, "
                   f"rejected={len(result.get('rejected_prices', []))}")
        return OrchestrateResponse(
            run_id=result.get("run_id", ""),
            supplier_updates=result.get("supplier_updates", []),
            approved_prices=result.get("approved_prices", []),
            rejected_prices=result.get("rejected_prices", []),
            cx_actions=result.get("cx_actions", []),
        )
    except Exception as e:
        # Log detailed error server-side (for debugging)
        logger.error(f"Orchestration error: {e}", exc_info=True)
        # Return generic error message to client (no information leakage)
        raise HTTPException(status_code=500, detail="Orchestration failed. Check server logs for details.")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
