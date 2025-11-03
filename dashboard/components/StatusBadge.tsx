"use client";

interface StatusBadgeProps {
  status: "approved" | "rejected" | "pending";
  label?: string;
}

export function StatusBadge({ status, label }: StatusBadgeProps) {
  const config = {
    approved: {
      className: "bg-green-50 text-green-900 border-green-200",
      defaultLabel: "Approved",
    },
    rejected: {
      className: "bg-red-50 text-red-900 border-red-200",
      defaultLabel: "Rejected",
    },
    pending: {
      className: "bg-yellow-50 text-yellow-900 border-yellow-200",
      defaultLabel: "Pending",
    },
  };

  const { className, defaultLabel } = config[status];

  return (
    <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium border ${className}`}>
      {label || defaultLabel}
    </span>
  );
}

