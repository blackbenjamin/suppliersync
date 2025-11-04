import { NextResponse } from "next/server";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const API_URL = process.env.ORCHESTRATOR_API_URL || "http://localhost:8000";

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = searchParams.get("limit") || "20";
    
    const response = await fetch(`${API_URL}/api/cx-events?limit=${limit}`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(5000),
      cache: "no-store",
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json(data.events || []);
  } catch (error: any) {
    console.error("CX events fetch error:", error);
    return NextResponse.json([], { status: 200 }); // Return empty array on error
  }
}
