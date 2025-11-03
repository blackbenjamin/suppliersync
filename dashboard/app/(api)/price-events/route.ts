
import { NextResponse } from "next/server";
import { query } from "@/lib/db";
export const runtime = "nodejs";

export async function GET() {
  const rows = query("SELECT * FROM price_events ORDER BY id DESC LIMIT 100");
  return NextResponse.json(rows);
}
