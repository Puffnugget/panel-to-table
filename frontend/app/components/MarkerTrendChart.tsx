"use client";

import { CartesianGrid, Line, LineChart, ReferenceArea, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { TIER_LABEL, type HistoryEntry } from "../lib/types";

export default function MarkerTrendChart({ entries, markerId }: { entries: HistoryEntry[]; markerId: string }) {
  const points = entries
    .map((entry) => {
      const result = entry.response.results.find((item) => item.id === markerId);
      if (!result) return null;
      return {
        date: entry.request.test_date,
        savedAt: entry.savedAt,
        value: result.value,
        unit: result.unit,
        status: TIER_LABEL[result.tier],
        bandLow: result.bar?.band_low,
        bandHigh: result.bar?.band_high,
      };
    })
    .filter((point): point is NonNullable<typeof point> => point !== null)
    .sort((a, b) => a.date.localeCompare(b.date) || a.savedAt.localeCompare(b.savedAt));

  if (!points.length) {
    return <p className="text-sm text-gray-600">This marker isn’t in the saved tests yet.</p>;
  }

  const seen = new Map<string, number>();
  const data = points.map((point) => {
    const count = (seen.get(point.date) || 0) + 1;
    seen.set(point.date, count);
    return { ...point, label: count === 1 ? point.date : `${point.date} (${count})` };
  });
  const latest = data[data.length - 1];
  const values = data.map((point) => point.value);
  const low = Math.min(latest.bandLow ?? latest.value, ...values);
  const high = Math.max(latest.bandHigh ?? latest.value, ...values);
  const pad = (high - low) * 0.15 || 1;

  return (
    <div>
      <div style={{ width: "100%", height: 320 }}>
        <ResponsiveContainer>
          <LineChart data={data} margin={{ top: 10, right: 16, bottom: 24, left: 0 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="label" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} domain={[low - pad, high + pad]} />
            {latest.bandLow != null && latest.bandHigh != null && (
              <ReferenceArea y1={latest.bandLow} y2={latest.bandHigh} fill="var(--leaf)" fillOpacity={0.45} />
            )}
            <Tooltip formatter={(value, _name, item) => [`${value} ${item.payload.unit} · ${item.payload.status}`, "Result"]} />
            <Line isAnimationActive={false} type="monotone" dataKey="value" stroke="#2C1810" strokeWidth={2} dot={{ r: 5, fill: "var(--clay-bright)", stroke: "#2C1810", strokeWidth: 1 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="text-sm text-gray-600">
        The shaded band is the usual range from the latest saved test that included this marker ({latest.unit}).
        {data.length < 2 ? " Add another test date to see a line." : ""}
      </p>
    </div>
  );
}
