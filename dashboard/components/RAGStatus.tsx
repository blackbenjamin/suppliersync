"use client";

import { useState, useEffect } from "react";

interface RAGStatus {
  has_docs_directory: boolean;
  has_vectorstore: boolean;
  docs_path: string;
  persist_path: string;
  document_count: number;  // Chunk count in vectorstore
  file_count?: number;  // Original file count
  chunk_count?: number;  // Chunk count (same as document_count)
  status: "ready" | "not_ready" | "error";
  message?: string;
}

export function RAGStatus() {
  const [status, setStatus] = useState<RAGStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [rebuilding, setRebuilding] = useState(false);

  const fetchStatus = async () => {
    try {
      // Add cache-busting parameter to ensure fresh data
      const res = await fetch(`/rag-status?t=${Date.now()}`, {
        cache: "no-store",
        headers: {
          "Cache-Control": "no-cache",
        },
      });
      if (!res.ok) {
        const errorText = await res.text();
        setStatus({ 
          status: "error", 
          message: `API error: ${res.status} ${errorText}`,
          has_docs_directory: false,
          has_vectorstore: false,
          docs_path: "",
          persist_path: "",
          document_count: 0
        } as RAGStatus);
        return;
      }
      const data = await res.json();
      setStatus(data);
    } catch (error: any) {
      console.error("RAG status fetch error:", error);
      setStatus({ 
        status: "error", 
        message: `Failed to fetch status: ${error.message || "Network error"}`,
        has_docs_directory: false,
        has_vectorstore: false,
        docs_path: "",
        persist_path: "",
        document_count: 0
      } as RAGStatus);
    } finally {
      setLoading(false);
    }
  };

  const handleRebuild = async () => {
    setRebuilding(true);
    try {
      const res = await fetch("/rag-rebuild", { method: "POST" });
      const data = await res.json();
      if (data.status === "success") {
        await fetchStatus(); // Refresh status
        const fileMsg = data.file_count !== undefined 
          ? `${data.file_count} files split into ${data.chunk_count || data.document_count} chunks`
          : `${data.document_count} documents indexed`;
        alert(`Vectorstore rebuilt successfully! ${fileMsg}.`);
      } else {
        alert(`Error: ${data.message}`);
      }
    } catch (error: any) {
      alert(`Error: ${error.message}`);
    } finally {
      setRebuilding(false);
    }
  };

  useEffect(() => {
    fetchStatus();
  }, []);

  if (loading) {
    return (
      <div className="rounded-lg border p-4">
        <p className="text-sm text-gray-600">Loading RAG status...</p>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="rounded-lg border p-4">
        <p className="text-sm text-red-600">Failed to load RAG status</p>
      </div>
    );
  }

  const isReady = status.status === "ready";

  return (
    <div className="rounded-lg border p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold">RAG Vectorstore Status</h3>
        <span
          className={`px-2 py-1 rounded text-xs font-medium ${
            isReady
              ? "bg-green-100 text-green-800"
              : "bg-yellow-100 text-yellow-800"
          }`}
        >
          {isReady ? "Ready" : "Not Ready"}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-gray-600">Documents Directory</p>
          <p className="font-mono text-xs">
            {status.has_docs_directory ? "✓" : "✗"} {status.docs_path}
          </p>
        </div>
        <div>
          <p className="text-gray-600">Vectorstore</p>
          <p className="font-mono text-xs">
            {status.has_vectorstore ? "✓" : "✗"} {status.persist_path}
          </p>
        </div>
        <div>
          <p className="text-gray-600">Document Count</p>
          <p className="font-semibold">
            {status.file_count !== undefined && status.file_count > 0 ? (
              <>
                {status.file_count} files{" "}
                <span className="text-gray-500 font-normal">
                  ({status.document_count} chunks)
                </span>
              </>
            ) : (
              status.document_count
            )}
          </p>
        </div>
        <div>
          <button
            onClick={handleRebuild}
            disabled={rebuilding}
            className="px-3 py-1 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 disabled:opacity-50"
          >
            {rebuilding ? "Rebuilding..." : "Rebuild Vectorstore"}
          </button>
        </div>
      </div>

      {status.message && (
        <p className="text-xs text-red-600">{status.message}</p>
      )}
      
      {status.status === "not_ready" && (
        <div className="text-xs text-yellow-600 space-y-1">
          <p>RAG is not ready. Possible reasons:</p>
          <ul className="list-disc list-inside ml-2">
            {!status.has_docs_directory && <li>Documents directory not found: {status.docs_path}</li>}
            {!status.has_vectorstore && <li>Vectorstore not found: {status.persist_path}</li>}
            {status.document_count === 0 && <li>No documents indexed (vectorstore is empty)</li>}
          </ul>
          <p className="mt-2">Click "Rebuild Vectorstore" to create the vectorstore from documents.</p>
        </div>
      )}
    </div>
  );
}

