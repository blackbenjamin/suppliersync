import { NextResponse } from "next/server";
export const runtime = "nodejs";
export const dynamic = "force-dynamic"; // Disable caching
export const revalidate = 0; // Disable revalidation

const API_URL = process.env.ORCHESTRATOR_API_URL || "http://localhost:8000";

export async function POST() {
  try {
    const response = await fetch(`${API_URL}/rag/rebuild`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(30000), // 30 second timeout
    });

    // Check content type before parsing
    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
      const text = await response.text();
      console.error(`RAG rebuild API returned non-JSON: ${contentType}`, text.substring(0, 200));
      return NextResponse.json(
        { 
          status: "error", 
          message: `API returned ${response.status} with content type ${contentType}. Check server logs.`,
          has_docs_directory: false,
          has_vectorstore: false,
          docs_path: "",
          persist_path: "",
          document_count: 0
        },
        { status: 500 }
      );
    }

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        const text = await response.text();
        errorData = { detail: text.substring(0, 200) };
      }
      console.error(`RAG rebuild API error: ${response.status}`, errorData);
      return NextResponse.json(
        { 
          status: "error", 
          message: errorData.detail || `API returned ${response.status}`,
          has_docs_directory: false,
          has_vectorstore: false,
          docs_path: "",
          persist_path: "",
          document_count: 0
        },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("RAG rebuild fetch error:", error);
    return NextResponse.json(
      { 
        status: "error", 
        message: error.message || "Failed to connect to orchestrator API",
        has_docs_directory: false,
        has_vectorstore: false,
        docs_path: "",
        persist_path: "",
        document_count: 0
      },
      { status: 500 }
    );
  }
}

