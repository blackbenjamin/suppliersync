import { NextResponse } from "next/server";
export const runtime = "nodejs";
export const dynamic = "force-dynamic"; // Disable caching
export const revalidate = 0; // Disable revalidation

const API_URL = process.env.ORCHESTRATOR_API_URL || "http://localhost:8000";

export async function GET() {
  try {
    console.log(`[RAG Status] Fetching from: ${API_URL}/rag/status`);
    
    const response = await fetch(`${API_URL}/rag/status`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      // Add timeout to prevent hanging
      signal: AbortSignal.timeout(10000), // Increased timeout
      cache: "no-store", // Disable fetch caching
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[RAG Status] API error: ${response.status} - ${errorText}`);
      // Return "not_available" status for 503 errors (RAG not available)
      if (response.status === 503) {
        return NextResponse.json({
          status: "not_available",
          has_docs_directory: false,
          has_vectorstore: false,
          docs_path: "",
          persist_path: "",
          document_count: 0,
          file_count: 0,
          message: "RAG dependencies not installed"
        });
      }
      // Return error response instead of throwing
      return NextResponse.json(
        { 
          status: "error", 
          message: `API returned ${response.status}: ${errorText}`,
          has_docs_directory: false,
          has_vectorstore: false,
          docs_path: "",
          persist_path: "",
          document_count: 0,
          file_count: 0
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    console.log(`[RAG Status] Success: ${JSON.stringify(data)}`);
    // Return with no-cache headers to prevent client-side caching
    return NextResponse.json(data, {
      headers: {
        "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
      },
    });
  } catch (error: any) {
    console.error("[RAG Status] Fetch error:", error.message);
    // Return error response instead of throwing
    return NextResponse.json(
      { 
        status: "error", 
        message: error.message || "Failed to connect to orchestrator API",
        has_docs_directory: false,
        has_vectorstore: false,
        docs_path: "",
        persist_path: "",
        document_count: 0,
        file_count: 0
      },
      { status: 200 } // Return 200 with error status in body
    );
  }
}

