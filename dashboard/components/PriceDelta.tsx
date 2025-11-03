
export default function PriceDelta({ prev, next }: { prev: number, next: number }) {
  const diff = next - prev;
  const pct = prev ? (diff/prev)*100 : 0;
  const sign = diff > 0 ? "+" : "";
  const color = diff === 0 ? "text-neutral-500" : diff > 0 ? "text-emerald-600" : "text-rose-600";
  return <span className={`text-sm ${color}`}>{sign}{diff.toFixed(2)} ({pct.toFixed(1)}%)</span>;
}
