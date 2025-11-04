import { NextResponse } from "next/server";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const API_URL = process.env.ORCHESTRATOR_API_URL || "http://localhost:8000";

export async function GET() {
  try {
    // Log API URL for debugging (remove in production)
    console.log(`[Metrics] Fetching from: ${API_URL}/api/metrics`);
    
    const response = await fetch(`${API_URL}/api/metrics`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(10000), // Increased timeout
      cache: "no-store",
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[Metrics] API error: ${response.status} - ${errorText}`);
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    console.log(`[Metrics] Success: ${JSON.stringify(data)}`);
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("[Metrics] Fetch error:", error.message);
    // Return default values instead of throwing
    return NextResponse.json({
      total_cost: 0,
      total_tokens: 0,
      avg_latency: 0,
      runs: [],
      error: error.message,
    });
  }
}

