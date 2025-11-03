
"use client";
import { ShoppingCart, RefreshCw } from "lucide-react";

export default function TopNav() {
  const run = async () => {
    const res = await fetch("/orchestrate", { method: "POST" });
    const j = await res.json();
    console.log(j);
    window.location.reload();
  };
  return (
    <div className="sticky top-0 z-10 bg-white/70 backdrop-blur border-b border-neutral-200">
      <div className="mx-auto max-w-7xl px-4 py-3 flex items-center gap-3">
        <ShoppingCart className="h-6 w-6 text-brand-600" />
        <div className="font-semibold">SupplierSync Console</div>
        <div className="ml-auto">
          <button onClick={run} className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-brand-600 text-white hover:opacity-90">
            <RefreshCw className="h-4 w-4"/> Run Orchestration
          </button>
        </div>
      </div>
    </div>
  );
}
