
"use client";
import { useState } from "react";
import { ShoppingCart, RefreshCw, Loader2 } from "lucide-react";

export default function TopNav() {
  const [isRunning, setIsRunning] = useState(false);

  const run = async () => {
    if (isRunning) return; // Prevent multiple clicks
    
    setIsRunning(true);
    try {
      const res = await fetch("/orchestrate", { method: "POST" });
      const j = await res.json();
      console.log(j);
      
      if (j.error) {
        console.error("Orchestration error:", j.error);
        alert(`Orchestration failed: ${j.error}`);
      } else {
        // Reload page to show new data
        window.location.reload();
      }
    } catch (error: any) {
      console.error("Orchestration error:", error);
      alert(`Failed to run orchestration: ${error.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="sticky top-0 z-10 bg-white/70 backdrop-blur border-b border-neutral-200">
      <div className="mx-auto max-w-7xl px-4 py-3 flex items-center gap-3">
        <ShoppingCart className="h-6 w-6 text-brand-600" />
        <div className="font-semibold">SupplierSync Console</div>
        <div className="ml-auto">
          <button 
            onClick={run} 
            disabled={isRunning}
            className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl text-white transition-all ${
              isRunning 
                ? "bg-brand-400 cursor-not-allowed" 
                : "bg-brand-600 hover:opacity-90"
            }`}
          >
            {isRunning ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" /> Running...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4"/> Run Orchestration
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
