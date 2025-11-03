
import { query } from "@/lib/db";

export default function StatsCards() {
  const [prod] = query("SELECT COUNT(*) as c FROM products WHERE is_active=1");
  const [events] = query("SELECT COUNT(*) as c FROM price_events");
  const [rejected] = query("SELECT COUNT(*) as c FROM rejected_prices");
  const [cx] = query("SELECT COUNT(*) as c FROM cx_events");
  return (
    <div className="grid grid-cols-2 gap-4">
      {[
        {label:"Active SKUs", value:prod?.c||0},
        {label:"Approved Price Events", value:events?.c||0},
        {label:"Rejected Prices", value:rejected?.c||0, color:"text-red-600"},
        {label:"CX Events", value:cx?.c||0}
      ].map((s,i)=> (
        <div key={i} className="card p-4">
          <div className="text-sm text-neutral-500">{s.label}</div>
          <div className={`text-3xl font-semibold ${s.color || ""}`}>{s.value}</div>
        </div>
      ))}
    </div>
  );
}
