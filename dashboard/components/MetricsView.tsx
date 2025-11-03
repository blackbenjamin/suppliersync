import { query } from "@/lib/db";
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
  // Get all agent logs
  const allLogs = query("SELECT * FROM agent_logs ORDER BY created_at DESC LIMIT 100") as AgentLog[];
  
  // Group by run_id
  const runsMap = new Map<string, RunSummary>();
  
  allLogs.forEach((log) => {
    if (!log.run_id) return;
    
    if (!runsMap.has(log.run_id)) {
      runsMap.set(log.run_id, {
        run_id: log.run_id,
        total_cost: 0,
        total_tokens_in: 0,
        total_tokens_out: 0,
        total_latency_ms: 0,
        agent_count: 0,
        created_at: log.created_at,
      });
    }
    
    const run = runsMap.get(log.run_id)!;
    run.total_cost += log.cost_usd || 0;
    run.total_tokens_in += log.tokens_in || 0;
    run.total_tokens_out += log.tokens_out || 0;
    run.total_latency_ms += log.latency_ms || 0;
    run.agent_count += 1;
  });
  
  const runs = Array.from(runsMap.values())
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 20);
  
  // Calculate agent performance averages
  const agentStats = new Map<string, { count: number; totalLatency: number; totalCost: number; totalTokensIn: number; totalTokensOut: number }>();
  
  allLogs.forEach((log) => {
    if (!agentStats.has(log.agent)) {
      agentStats.set(log.agent, { count: 0, totalLatency: 0, totalCost: 0, totalTokensIn: 0, totalTokensOut: 0 });
    }
    const stats = agentStats.get(log.agent)!;
    stats.count += 1;
    stats.totalLatency += log.latency_ms || 0;
    stats.totalCost += log.cost_usd || 0;
    stats.totalTokensIn += log.tokens_in || 0;
    stats.totalTokensOut += log.tokens_out || 0;
  });
  
  const agentPerformance = Array.from(agentStats.entries()).map(([agent, stats]) => ({
    agent,
    avgLatency: stats.totalLatency / stats.count,
    totalCost: stats.totalCost,
    avgCost: stats.totalCost / stats.count,
    totalTokensIn: stats.totalTokensIn,
    totalTokensOut: stats.totalTokensOut,
    callCount: stats.count,
  }));
  
  // Calculate totals
  const totalCost = allLogs.reduce((sum, log) => sum + (log.cost_usd || 0), 0);
  const totalTokens = allLogs.reduce((sum, log) => sum + (log.tokens_in || 0) + (log.tokens_out || 0), 0);
  const avgLatency = allLogs.length > 0 
    ? allLogs.reduce((sum, log) => sum + (log.latency_ms || 0), 0) / allLogs.length 
    : 0;
  
  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="text-sm text-neutral-500">Total Cost</div>
          <div className="text-2xl font-semibold text-blue-600">${totalCost.toFixed(4)}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-neutral-500">Total Tokens</div>
          <div className="text-2xl font-semibold">{totalTokens.toLocaleString()}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-neutral-500">Avg Latency</div>
          <div className="text-2xl font-semibold">{avgLatency.toFixed(0)}ms</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-neutral-500">Total Runs</div>
          <div className="text-2xl font-semibold">{runs.length}</div>
        </div>
      </div>
      
      {/* Agent Performance */}
      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Agent Performance</h2>
        <div className="card overflow-hidden">
          <table className="min-w-full text-sm">
            <thead className="bg-neutral-100">
              <tr>
                <th className="text-left px-3 py-2 font-medium text-neutral-700">Agent</th>
                <th className="text-left px-3 py-2 font-medium text-neutral-700">Calls</th>
                <th className="text-left px-3 py-2 font-medium text-neutral-700">Avg Latency</th>
                <th className="text-left px-3 py-2 font-medium text-neutral-700">Total Cost</th>
                <th className="text-left px-3 py-2 font-medium text-neutral-700">Tokens In</th>
                <th className="text-left px-3 py-2 font-medium text-neutral-700">Tokens Out</th>
              </tr>
            </thead>
            <tbody>
              {agentPerformance.map((ap) => (
                <tr key={ap.agent} className="border-t">
                  <td className="px-3 py-2 font-medium capitalize">{ap.agent}</td>
                  <td className="px-3 py-2">{ap.callCount}</td>
                  <td className="px-3 py-2">{ap.avgLatency.toFixed(0)}ms</td>
                  <td className="px-3 py-2 font-medium text-blue-600">${ap.totalCost.toFixed(4)}</td>
                  <td className="px-3 py-2 text-neutral-600">{ap.totalTokensIn.toLocaleString()}</td>
                  <td className="px-3 py-2 text-neutral-600">{ap.totalTokensOut.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
      
      {/* Recent Runs */}
      <section className="space-y-2">
        <h2 className="text-lg font-semibold">Recent Orchestration Runs</h2>
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
              {runs.map((run) => (
                <tr key={run.run_id} className="border-t">
                  <td className="px-3 py-2 font-mono text-xs">{run.run_id.substring(0, 8)}...</td>
                  <td className="px-3 py-2">{run.agent_count}</td>
                  <td className="px-3 py-2 font-medium text-blue-600">${run.total_cost.toFixed(4)}</td>
                  <td className="px-3 py-2 text-neutral-600">
                    {(run.total_tokens_in + run.total_tokens_out).toLocaleString()}
                  </td>
                  <td className="px-3 py-2">{run.total_latency_ms}ms</td>
                  <td className="px-3 py-2 text-xs text-neutral-500">
                    {formatEasternTime(run.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {runs.length === 0 && (
            <div className="p-6 text-center text-neutral-500">
              No orchestration runs yet. Run an orchestration to see metrics.
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

