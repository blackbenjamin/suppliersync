"use client";

import { formatEasternTime } from "@/lib/dateUtils";

interface RejectedPrice {
  id: number;
  sku: string;
  proposed_price: number;
  current_price: number | null;
  reject_reason: string;
  reject_details: string | null;
  run_id: string | null;
  created_at: string;
}

interface GovernanceTableProps {
  rejectedPrices: RejectedPrice[];
}

const REJECTION_COLORS: Record<string, string> = {
  retail_below_wholesale: "bg-red-50 text-red-900",
  margin_below_minimum: "bg-orange-50 text-orange-900",
  daily_drift_exceeded: "bg-yellow-50 text-yellow-900",
  below_map_price: "bg-purple-50 text-purple-900",
  category_blocked: "bg-pink-50 text-pink-900",
  category_not_allowed: "bg-pink-50 text-pink-900",
  invalid_price_format: "bg-gray-50 text-gray-900",
  price_must_be_positive: "bg-gray-50 text-gray-900",
  missing_sku: "bg-gray-50 text-gray-900",
};

const REJECTION_LABELS: Record<string, string> = {
  retail_below_wholesale: "Below Wholesale",
  margin_below_minimum: "Low Margin",
  daily_drift_exceeded: "Exceeds Daily Limit",
  below_map_price: "Below MAP",
  category_blocked: "Category Blocked",
  category_not_allowed: "Category Not Allowed",
  invalid_price_format: "Invalid Format",
  price_must_be_positive: "Invalid Price",
  missing_sku: "Missing SKU",
};

function getStatusBadge(reason: string) {
  const colorClass = REJECTION_COLORS[reason] || "bg-gray-50 text-gray-900";
  const label = REJECTION_LABELS[reason] || reason;
  return (
    <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${colorClass}`}>
      {label}
    </span>
  );
}

export function GovernanceTable({ rejectedPrices }: GovernanceTableProps) {
  if (rejectedPrices.length === 0) {
    return (
      <div className="card p-6 text-center text-neutral-500">
        No rejected price changes. All proposals passed governance checks.
      </div>
    );
  }

  return (
    <div className="card overflow-hidden">
      <table className="min-w-full text-sm">
        <thead className="bg-neutral-100">
          <tr>
            <th className="text-left px-3 py-2 font-medium text-neutral-700">SKU</th>
            <th className="text-left px-3 py-2 font-medium text-neutral-700">Current ($)</th>
            <th className="text-left px-3 py-2 font-medium text-neutral-700">Proposed ($)</th>
            <th className="text-left px-3 py-2 font-medium text-neutral-700">Change</th>
            <th className="text-left px-3 py-2 font-medium text-neutral-700">Reason</th>
            <th className="text-left px-3 py-2 font-medium text-neutral-700">Details</th>
            <th className="text-left px-3 py-2 font-medium text-neutral-700">When</th>
          </tr>
        </thead>
        <tbody>
          {rejectedPrices.map((r) => {
            const current = r.current_price ?? 0;
            const proposed = r.proposed_price;
            const changePct = current > 0 ? ((proposed - current) / current) * 100 : 0;
            const changeColor = changePct > 0 ? "text-red-600" : "text-green-600";
            const changeSymbol = changePct > 0 ? "+" : "";

            return (
              <tr key={r.id} className="border-t">
                <td className="px-3 py-2 font-mono text-xs">{r.sku}</td>
                <td className="px-3 py-2">${current.toFixed(2)}</td>
                <td className="px-3 py-2 font-medium">${proposed.toFixed(2)}</td>
                <td className={`px-3 py-2 ${changeColor}`}>
                  {changeSymbol}{changePct.toFixed(1)}%
                </td>
                <td className="px-3 py-2">{getStatusBadge(r.reject_reason)}</td>
                <td className="px-3 py-2 text-xs text-neutral-600 max-w-xs truncate" title={r.reject_details || ""}>
                  {r.reject_details || "-"}
                </td>
                <td className="px-3 py-2 text-xs text-neutral-500">
                  {formatEasternTime(r.created_at)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

