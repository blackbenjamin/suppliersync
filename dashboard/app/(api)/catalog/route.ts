
import { NextResponse } from "next/server";
import { query } from "@/lib/db";
export const runtime = "nodejs";

export async function GET() {
  const rows = query("SELECT * FROM products WHERE is_active=1 ORDER BY sku");
  return NextResponse.json(rows);
}
