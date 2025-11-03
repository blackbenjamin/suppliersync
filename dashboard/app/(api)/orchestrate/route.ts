
import { NextResponse } from "next/server";
export const runtime = "nodejs";

const API_URL = process.env.ORCHESTRATOR_API_URL || "http://localhost:8000";

export async function POST() {
  try {
    const response = await fetch(`${API_URL}/orchestrate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      // Timeout after 120 seconds (orchestration can take a while)
      signal: AbortSignal.timeout(120_000),
    });

    if (!response.ok) {
      const error = await response.text();
      return NextResponse.json(
        { error: `Orchestrator API error: ${response.status} ${error}` },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json({
      success: true,
      run_id: data.run_id,
      supplier_updates: data.supplier_updates,
      approved_prices: data.approved_prices,
      rejected_prices: data.rejected_prices,
      cx_actions: data.cx_actions,
    });
  } catch (error: any) {
    if (error.name === "TimeoutError" || error.name === "AbortError") {
      return NextResponse.json(
        { error: "Orchestration timed out after 120 seconds" },
        { status: 504 }
      );
    }
    return NextResponse.json(
      { error: `Failed to call orchestrator API: ${error.message}` },
      { status: 500 }
    );
  }
}
