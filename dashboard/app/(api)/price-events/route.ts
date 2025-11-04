import { NextResponse } from "next/server";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const API_URL = process.env.ORCHESTRATOR_API_URL || "http://localhost:8000";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = searchParams.get("limit") || "20";
    
    console.log(`[Price Events] Fetching from: ${API_URL}/api/price-events?limit=${limit}`);
    
    const response = await fetch(`${API_URL}/api/price-events?limit=${limit}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(10000), // Increased timeout
      cache: "no-store",
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`[Price Events] API error: ${response.status} - ${errorText}`);
      throw new Error(`API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    console.log(`[Price Events] Success: ${data.events?.length || 0} events`);
    return NextResponse.json(data.events || []);
  } catch (error: any) {
    console.error("[Price Events] Fetch error:", error.message);
    return NextResponse.json([], { status: 200 }); // Return empty array on error
  }
}
