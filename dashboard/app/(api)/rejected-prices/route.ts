import { NextResponse } from "next/server";
import { query } from "@/lib/db";
export const runtime = "nodejs";

export async function GET() {
  const rows = query("SELECT * FROM rejected_prices ORDER BY id DESC LIMIT 50");
  return NextResponse.json(rows);
}

