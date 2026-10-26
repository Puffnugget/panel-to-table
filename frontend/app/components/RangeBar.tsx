import type { RangeBarData } from "../lib/types";

export function RangeBar({ bar, label }: { bar: RangeBarData; label: string }) {
  const span = bar.max - bar.min || 1;
  const pct = (value: number) => ((value - bar.min) / span) * 100;
  const dot = Math.min(100, Math.max(0, pct(bar.value)));
  return (
    <div className="mt-3" role="img" aria-label={label}>
      <div className="range-track">
        {bar.zones.map((zone, index) => (
          <div
            key={`${zone.tier}-${index}`}
            className={`zone zone-${zone.tier}`}
            style={{ left: `${pct(zone.start)}%`, width: `${Math.max(0, pct(zone.end) - pct(zone.start))}%` }}
          />
        ))}
        <div className="range-dot" style={{ left: `${dot}%` }} />
      </div>
    </div>
  );
}
