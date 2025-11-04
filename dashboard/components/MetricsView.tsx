"use client";

import { useEffect, useState } from "react";
import { formatEasternTime } from "@/lib/dateUtils";

interface AgentLog {
  id: number;
  agent: string;
  step: string;
  tokens_in: number;
  tokens_out: number;
  latency_ms: number;
  cost_usd: number;
  run_id: string;
  created_at: string;
}

interface RunSummary {
  run_id: string;
  total_cost: number;
  total_tokens_in: number;
  total_tokens_out: number;
  total_latency_ms: number;
  agent_count: number;
  created_at: string;
}

export function MetricsView() {
  const [metrics, setMetrics] = useState({
    total_cost: 0,
    total_tokens: 0,
    avg_latency: 0,
    runs: [] as any[],
  });
  const [agentPerformance, setAgentPerformance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const API_URL = process.env.NEXT_PUBLIC_ORCHESTRATOR_API_URL || process.env.ORCHESTRATOR_API_URL || "http://localhost:8000";
        const response = await fetch(`${API_URL}/api/metrics`, {
          cache: "no-store",
        });

        if (response.ok) {
          const data = await response.json();
          setMetrics(data);
          
          // Calculate agent performance from runs
          // This is a simplified version - in production you'd want a dedicated endpoint
          const agentStats = new Map<string, { count: number; totalLatency: number; totalCost: number; totalTokens: number }>();
          
          // Note: We'd need agent-level data, but for now we'll show run-level data
          setAgentPerformance([]);
        }
      } catch (error) {
        console.error("Failed to fetch metrics:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="text-sm text-neutral-500">Total Cost</div>
          <div className="text-2xl font-semibold text-blue-600">
            {loading ? "..." : `$${metrics.total_cost.toFixed(4)}`}
          </div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-neutral-500">Total Tokens</div>
          <div className="text-2xl font-semibold">
            {loading ? "..." : metrics.total_tokens.toLocaleString()}
          </div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-neutral-500">Avg Latency</div>
          <div className="text-2xl font-semibold">
            {loading ? "..." : `${(metrics.avg_latency * 1000).toFixed(0)}ms`}
          </div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-neutral-500">Total Runs</div>
          <div className="text-2xl font-semibold">
            {loading ? "..." : metrics.runs.length}
          </div>
        </div>
      </div>

      {/* Recent Runs */}
      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Recent Orchestration Runs</h2>
        {loading ? (
          <div className="card p-4 text-center text-neutral-500">Loading...</div>
        ) : (
          <div className="card overflow-hidden">
            <table className="min-w-full text-sm">
              <thead className="bg-neutral-100">
                <tr>
                  <th className="text-left px-3 py-2 font-medium text-neutral-700">Run ID</th>
                  <th className="text-left px-3 py-2 font-medium text-neutral-700">Agents</th>
                  <th className="text-left px-3 py-2 font-medium text-neutral-700">Total Cost</th>
                  <th className="text-left px-3 py-2 font-medium text-neutral-700">Tokens</th>
                  <th className="text-left px-3 py-2 font-medium text-neutral-700">Latency</th>
                  <th className="text-left px-3 py-2 font-medium text-neutral-700">When</th>
                </tr>
              </thead>
              <tbody>
                {metrics.runs.map((run: any) => (
                  <tr key={run.run_id} className="border-t">
                    <td className="px-3 py-2 font-mono text-xs">{run.run_id?.substring(0, 8)}...</td>
                    <td className="px-3 py-2">{run.agent_count || "-"}</td>
                    <td className="px-3 py-2 font-medium text-blue-600">
                      ${(run.total_cost || 0).toFixed(4)}
                    </td>
                    <td className="px-3 py-2 text-neutral-600">
                      {(run.total_tokens || 0).toLocaleString()}
                    </td>
                    <td className="px-3 py-2">
                      {run.avg_latency_ms ? `${run.avg_latency_ms.toFixed(0)}ms` : "-"}
                    </td>
                    <td className="px-3 py-2 text-xs text-neutral-500">
                      {run.created_at ? formatEasternTime(run.created_at) : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {metrics.runs.length === 0 && (
              <div className="p-6 text-center text-neutral-500">
                No orchestration runs yet. Run an orchestration to see metrics.
              </div>
            )}
          </div>
        )}
      </section>
    </div>
  );
}
