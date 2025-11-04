"use client";

import { useEffect, useState } from "react";
import TopNav from "@/components/TopNav";
import StatsCards from "@/components/StatsCards";
import { DataTable } from "@/components/DataTable";
import PriceDelta from "@/components/PriceDelta";
import { GovernanceTable } from "@/components/GovernanceTable";
import { StatusBadge } from "@/components/StatusBadge";
import { MetricsView } from "@/components/MetricsView";
import { RAGStatus } from "@/components/RAGStatus";
import { formatEasternTime } from "@/lib/dateUtils";

export default function Page() {
  const [catalog, setCatalog] = useState<any[]>([]);
  const [priceEvents, setPriceEvents] = useState<any[]>([]);
  const [rejectedPrices, setRejectedPrices] = useState<any[]>([]);
  const [cxEvents, setCxEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch all data in parallel
        const [catalogRes, priceRes, rejectedRes, cxRes] = await Promise.all([
          fetch("/catalog", { cache: "no-store" }),
          fetch("/price-events", { cache: "no-store" }),
          fetch("/rejected-prices", { cache: "no-store" }),
          fetch("/cx-events", { cache: "no-store" }),
        ]);

        if (catalogRes.ok) {
          const data = await catalogRes.json();
          setCatalog(data);
        }
        if (priceRes.ok) {
          const data = await priceRes.json();
          setPriceEvents(data);
        }
        if (rejectedRes.ok) {
          const data = await rejectedRes.json();
          setRejectedPrices(data);
        }
        if (cxRes.ok) {
          const data = await cxRes.json();
          setCxEvents(data);
        }
      } catch (error) {
        console.error("Failed to fetch data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <TopNav />
      <main className="mx-auto max-w-7xl px-4 py-6 space-y-6">
        <StatsCards />

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
          {loading ? (
            <div className="card p-4 text-center text-neutral-500">Loading...</div>
          ) : (
            <DataTable
              rows={catalog}
              columns={[
                { key: "sku", label: "SKU" },
                { key: "name", label: "Name" },
                { key: "category", label: "Category" },
                { key: "wholesale_price", label: "Wholesale ($)" },
                { key: "retail_price", label: "Retail ($)" },
              ]}
            />
          )}
        </section>

        <section className="space-y-2">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold">Recent Price Events</h2>
            <StatusBadge status="approved" />
          </div>
          {loading ? (
            <div className="card p-4 text-center text-neutral-500">Loading...</div>
          ) : (
            <DataTable
              rows={priceEvents}
              columns={[
                { key: "id", label: "#" },
                { key: "sku", label: "SKU" },
                { key: "prev_price", label: "Prev ($)" },
                { key: "new_price", label: "New ($)" },
                { key: "reason", label: "Reason" },
                { key: "created_at", label: "When", render: (v) => formatEasternTime(v as string) },
                {
                  key: "new_price",
                  label: "Δ",
                  render: (_v, row: any) => <PriceDelta prev={row.prev_price} next={row.new_price} />,
                },
              ]}
            />
          )}
        </section>

        <section className="space-y-2">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold">Governance Decisions</h2>
            <StatusBadge status="rejected" />
          </div>
          {loading ? (
            <div className="card p-4 text-center text-neutral-500">Loading...</div>
          ) : (
            <GovernanceTable rejectedPrices={rejectedPrices as any} />
          )}
        </section>

        <section className="space-y-2">
          <h2 className="text-lg font-semibold">CX Events</h2>
          {loading ? (
            <div className="card p-4 text-center text-neutral-500">Loading...</div>
          ) : (
            <DataTable
              rows={cxEvents}
              columns={[
                { key: "id", label: "#" },
                { key: "sku", label: "SKU" },
                { key: "event_type", label: "Type" },
                { key: "details", label: "Details" },
                { key: "created_at", label: "When", render: (v) => formatEasternTime(v as string) },
              ]}
            />
          )}
        </section>
      </main>
    </div>
  );
}
