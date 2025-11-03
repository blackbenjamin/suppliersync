
import { formatEasternTime } from "@/lib/dateUtils";

export function DataTable<T>({ rows, columns }: { rows: T[]; columns: { key: keyof T; label: string; render?: (v:any, row:T)=>any }[] }) {
  return (
    <div className="card overflow-hidden">
      <table className="min-w-full text-sm">
        <thead className="bg-neutral-100">
          <tr>
            {columns.map(c=> <th key={String(c.key)} className="text-left px-3 py-2 font-medium text-neutral-700">{c.label}</th>)}
          </tr>
        </thead>
        <tbody>
          {rows.map((r,i)=> (
            <tr key={i} className="border-t">
              {columns.map(c=> <td key={String(c.key)} className="px-3 py-2">{c.render? c.render((r as any)[c.key], r) : (r as any)[c.key]}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
