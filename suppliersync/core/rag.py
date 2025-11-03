
import os, chromadb
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

EMB = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def build_vectorstore(path: str="data/docs", persist: str=".chroma", clear_existing: bool=True, collection_name: str="langchain"):
    """
    Build RAG vectorstore from documents.
    
    Security: Validates paths to prevent path traversal attacks.
    Uses security utilities for path validation.
    """
    # Validate and sanitize paths to prevent path traversal
    # Use security utilities for proper validation
    try:
        from core.security import validate_path
        base_dir = os.getcwd()
        path = validate_path(path, base_dir=base_dir, allow_absolute=False)
        persist = validate_path(persist, base_dir=base_dir, allow_absolute=False)
    except (ValueError, ImportError) as e:
        raise ValueError(f"Invalid path: {e}")
    
    # Ensure paths are within allowed directories (defense in depth)
    # In production, restrict to specific allowed directories
    if not os.path.isdir(path):
        return None
    docs = []
    def loader_cls(p): 
        return PyPDFLoader(p) if p.lower().endswith(".pdf") else TextLoader(p)
    loader = DirectoryLoader(path, glob="**/*", use_multithreading=True, loader_cls=loader_cls)
    for d in loader.load():
        docs.append(d)
    
    # Clear existing collection if requested (for rebuild)
    if clear_existing:
        try:
            # Delete all collections to ensure clean state (using ChromaDB API directly)
            try:
                client = chromadb.PersistentClient(path=persist)
                collections = client.list_collections()
                for col in collections:
                    print(f"Deleting collection: {col.name} ({col.count()} documents)")
                    client.delete_collection(col.name)
                print(f"Deleted {len(collections)} existing collection(s) via ChromaDB API")
            except Exception as e1:
                print(f"Could not delete via ChromaDB API: {e1}")
                # Fallback: try to delete directory directly
                import shutil
                import time
                if os.path.exists(persist):
                    # Wait a bit for any locks to release
                    time.sleep(0.5)
                    if os.path.isdir(persist):
                        print(f"Deleting existing vectorstore directory: {persist}")
                        shutil.rmtree(persist)
                        print(f"Successfully deleted vectorstore directory")
                    elif os.path.isfile(persist):
                        print(f"Deleting existing vectorstore file: {persist}")
                        os.remove(persist)
                        print(f"Successfully deleted vectorstore file")
        except Exception as e:
            print(f"Warning: Could not clear existing vectorstore: {e}")
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    chunks = splitter.split_documents(docs)
    
    # Create new vectorstore with explicit collection name
    vs = Chroma.from_documents(
        chunks, 
        EMB, 
        persist_directory=persist,
        collection_name=collection_name
    )
    vs.persist()
    return vs, len(docs), len(chunks)  # Return original doc count and chunk count
