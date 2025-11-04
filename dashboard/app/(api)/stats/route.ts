import { NextResponse } from "next/server";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const API_URL = process.env.ORCHESTRATOR_API_URL || "http://localhost:8000";

export async function GET() {
  try {
    // Log API URL for debugging (remove in production)
    console.log(`[Stats] Fetching from: ${API_URL}/api/stats`);
    
    const response = await fetch(`${API_URL}/api/stats`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(10000), // Increased timeout
      cache: "no-store",
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[Stats] API error: ${response.status} - ${errorText}`);
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    console.log(`[Stats] Success: ${JSON.stringify(data)}`);
    return NextResponse.json(data);
  } catch (error: any) {
    console.error("[Stats] Fetch error:", error.message);
    // Return default values instead of throwing
    return NextResponse.json({
      active_skus: 0,
      approved_price_events: 0,
      rejected_prices: 0,
      cx_events: 0,
      error: error.message,
    });
  }
}

