
import TopNav from "@/components/TopNav";
import StatsCards from "@/components/StatsCards";
import { DataTable } from "@/components/DataTable";
import PriceDelta from "@/components/PriceDelta";
import { GovernanceTable } from "@/components/GovernanceTable";
import { StatusBadge } from "@/components/StatusBadge";
import { MetricsView } from "@/components/MetricsView";
import { RAGStatus } from "@/components/RAGStatus";
import { query } from "@/lib/db";
import { formatEasternTime } from "@/lib/dateUtils";

export const runtime = "nodejs";
export const dynamic = "force-dynamic"; // Prevent static generation during build

export default function Page() {
  // Query database - will only run at request time, not during build
  let catalog: any[] = [];
  let priceEvents: any[] = [];
  let rejectedPrices: any[] = [];
  let cxEvents: any[] = [];
  
  try {
    catalog = query("SELECT sku, name, category, wholesale_price, retail_price FROM products WHERE is_active=1 ORDER BY sku");
    priceEvents = query("SELECT * FROM price_events ORDER BY id DESC LIMIT 20");
    rejectedPrices = query("SELECT * FROM rejected_prices ORDER BY id DESC LIMIT 20");
    cxEvents = query("SELECT * FROM cx_events ORDER BY id DESC LIMIT 20");
  } catch (error: any) {
    // Database not available yet (e.g., during build or initialization)
    console.error("Database query error:", error.message);
  }

  return (
    <div>
      <TopNav/>
      <main className="mx-auto max-w-7xl px-4 py-6 space-y-6">
        <StatsCards/>
        
        <section className="space-y-2">
          <h2 className="text-lg font-semibold">Metrics & Observability</h2>
          <MetricsView />
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-semibold">RAG Status</h2>
          <RAGStatus />
        </section>
        
        <section className="space-y-2">
          <h2 className="text-lg font-semibold">Catalog</h2>
          <DataTable rows={catalog} columns={[
            { key: "sku", label: "SKU" },
            { key: "name", label: "Name" },
            { key: "category", label: "Category" },
            { key: "wholesale_price", label: "Wholesale ($)" },
            { key: "retail_price", label: "Retail ($)" },
          ]} />
        </section>

        <section className="space-y-2">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold">Recent Price Events</h2>
            <StatusBadge status="approved" />
          </div>
          <DataTable rows={priceEvents} columns={[
            { key: "id", label: "#" },
            { key: "sku", label: "SKU" },
            { key: "prev_price", label: "Prev ($)" },
            { key: "new_price", label: "New ($)" },
            { key: "reason", label: "Reason" },
            { key: "created_at", label: "When", render: (v) => formatEasternTime(v as string) },
            { key: "new_price", label: "Δ", render: (_v, row:any) => <PriceDelta prev={row.prev_price} next={row.new_price}/> },
          ]} />
        </section>

        <section className="space-y-2">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold">Governance Decisions</h2>
            <StatusBadge status="rejected" />
          </div>
          <GovernanceTable rejectedPrices={rejectedPrices as any} />
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-semibold">CX Events</h2>
          <DataTable rows={cxEvents} columns={[
            { key: "id", label: "#" },
            { key: "sku", label: "SKU" },
            { key: "event_type", label: "Type" },
            { key: "details", label: "Details" },
            { key: "created_at", label: "When", render: (v) => formatEasternTime(v as string) },
          ]} />
        </section>
      </main>
    </div>
  );
}
