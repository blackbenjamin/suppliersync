import { NextResponse } from "next/server";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const API_URL = process.env.ORCHESTRATOR_API_URL || "http://localhost:8000";

export async function GET() {
  try {
    console.log(`[Catalog] Fetching from: ${API_URL}/api/catalog`);
    
    const response = await fetch(`${API_URL}/api/catalog`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(10000), // Increased timeout
      cache: "no-store",
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[Catalog] API error: ${response.status} - ${errorText}`);
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    console.log(`[Catalog] Success: ${data.products?.length || 0} products`);
    return NextResponse.json(data.products || []);
  } catch (error: any) {
    console.error("[Catalog] Fetch error:", error.message);
    // Return empty array on error so UI doesn't break
    return NextResponse.json([], { status: 200 });
  }
}
