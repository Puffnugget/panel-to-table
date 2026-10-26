import { historyFile } from "../lib/history";
import { TIER_LABEL, type HistoryEntry, type MarkerResult } from "../lib/types";

function download(filename: string, blob: Blob) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function csvCell(value: string | number) {
  const text = String(value ?? "");
  if (/[",\n]/.test(text)) return `"${text.replaceAll('"', '""')}"`;
  return text;
}

function toCsv(results: MarkerResult[]) {
  const rows = [
    ["Marker", "Value", "Unit", "Status", "Direction", "Message", "Foods"],
    ...results.map((result) => [
      result.name,
      result.value,
      result.unit,
      TIER_LABEL[result.tier],
      result.direction ?? "",
      result.message,
      result.foods.join("; "),
    ]),
  ];
  return rows.map((row) => row.map(csvCell).join(",")).join("\n");
}

export function ExportSection({
  entries,
  current,
  onImport,
}: {
  entries: HistoryEntry[];
  current: HistoryEntry | null;
  onImport: (file: File) => void;
}) {
  return (
    <section className="card p-5">
      <h2 className="text-2xl font-semibold">Take the results with you</h2>
      <p className="mt-1 text-sm text-gray-600">JSON restores the saved tests on another device. CSV is the result on screen, for a spreadsheet.</p>
      <div className="mt-4 flex flex-col sm:flex-row gap-3">
        <button
          className="btn"
          type="button"
          onClick={() => download("panel-to-table-history.json", new Blob([JSON.stringify(historyFile(entries), null, 2)], { type: "application/json" }))}
          disabled={!entries.length}
        >
          Download JSON
        </button>
        <button
          className="btn"
          type="button"
          onClick={() => {
            if (!current) return;
            download("panel-to-table-results.csv", new Blob([toCsv(current.response.results)], { type: "text/csv" }));
          }}
          disabled={!current}
        >
          Download CSV
        </button>
        <label className="btn text-center cursor-pointer">
          Import JSON
          <input
            className="hidden"
            type="file"
            accept="application/json,.json"
            onChange={(event) => {
              const file = event.target.files?.[0];
              event.target.value = "";
              if (file) onImport(file);
            }}
          />
        </label>
      </div>
    </section>
  );
}
