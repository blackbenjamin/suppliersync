"use client";

import { useEffect, useState } from "react";

export default function StatsCards() {
  const [stats, setStats] = useState({
    active_skus: 0,
    approved_price_events: 0,
    rejected_prices: 0,
    cx_events: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch("/stats", {
          cache: "no-store",
        });
        
        if (!res.ok) {
          const errorData = await res.json().catch(() => ({}));
          throw new Error(`HTTP ${res.status}: ${errorData.error || res.statusText}`);
        }
        
        const data = await res.json();
        setStats(data);
        setError(null);
      } catch (err: any) {
        console.error("Failed to fetch stats:", err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    // Refresh every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-2 gap-4">
      {error && (
        <div className="col-span-2 card p-4 bg-red-50 border border-red-200">
          <div className="text-sm text-red-600 font-medium">Error loading stats</div>
          <div className="text-xs text-red-500 mt-1">{error}</div>
        </div>
      )}
      {[
        { label: "Active SKUs", value: stats.active_skus },
        { label: "Approved Price Events", value: stats.approved_price_events },
        { label: "Rejected Prices", value: stats.rejected_prices, color: "text-red-600" },
        { label: "CX Events", value: stats.cx_events },
      ].map((s, i) => (
        <div key={i} className="card p-4">
          <div className="text-sm text-neutral-500">{s.label}</div>
          <div className={`text-3xl font-semibold ${s.color || ""}`}>
            {loading ? "..." : s.value}
          </div>
        </div>
      ))}
    </div>
  );
}
