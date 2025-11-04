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

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch("/stats", {
          cache: "no-store",
        });
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (error) {
        console.error("Failed to fetch stats:", error);
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
