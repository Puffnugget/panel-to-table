import { TIER_LABEL, type HistoryEntry, type Tier } from "../lib/types";

function summary(entry: HistoryEntry) {
  const counts = new Map<string, number>();
  for (const result of entry.response.results) {
    counts.set(result.tier, (counts.get(result.tier) || 0) + 1);
  }
  const order: Tier[] = ["see_doctor", "out_of_range", "borderline", "in_range", "unrated"];
  return order
    .filter((tier) => counts.get(tier))
    .map((tier) => `${counts.get(tier)} ${TIER_LABEL[tier].toLowerCase()}`)
    .join(", ");
}

export function HistoryList({
  entries,
  activeId,
  onOpen,
  onRemove,
}: {
  entries: HistoryEntry[];
  activeId: string | null;
  onOpen: (entry: HistoryEntry) => void;
  onRemove: (id: string) => void;
}) {
  if (!entries.length) {
    return <p className="text-sm text-gray-600">No saved tests yet. A finished analysis is kept in this browser.</p>;
  }
  const ordered = [...entries].sort((a, b) => b.request.test_date.localeCompare(a.request.test_date));
  return (
    <ul className="space-y-2">
      {ordered.map((entry) => (
        <li key={entry.id} className="flex flex-wrap items-center justify-between gap-2 border border-[var(--mint-light)] rounded-lg p-3">
          <div>
            <p className="font-medium">{entry.request.name ? `${entry.request.name} · ${entry.request.test_date}` : entry.request.test_date}</p>
            <p className="text-sm text-gray-600">
              Age {entry.request.age}, {entry.request.sex}, {entry.request.fasting ? "fasting" : "not fasting"}. {summary(entry)}
            </p>
          </div>
          <div className="flex gap-2">
            <button className="btn" type="button" onClick={() => onOpen(entry)} aria-current={entry.id === activeId ? "true" : undefined}>
              {entry.id === activeId ? "Showing" : "Open"}
            </button>
            <button className="btn btn-secondary" type="button" onClick={() => onRemove(entry.id)}>Remove</button>
          </div>
        </li>
      ))}
    </ul>
  );
}
