import type { HistoryEntry } from "./types";

const KEY = "panel-to-table.history.v1";
const LEGACY_KEY = "flexgene.history.v1";

function isEntry(value: unknown): value is HistoryEntry {
  if (!value || typeof value !== "object") return false;
  const entry = value as HistoryEntry;
  return Boolean(
    typeof entry.id === "string" &&
      entry.request &&
      Array.isArray(entry.request.markers) &&
      entry.response &&
      Array.isArray(entry.response.results),
  );
}

export function loadHistory(): HistoryEntry[] {
  try {
    let raw = localStorage.getItem(KEY);
    if (!raw) {
      raw = localStorage.getItem(LEGACY_KEY);
      if (raw) {
        localStorage.setItem(KEY, raw);
        localStorage.removeItem(LEGACY_KEY);
      }
    }
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    const entries = Array.isArray(parsed) ? parsed : parsed?.entries;
    if (!Array.isArray(entries)) return [];
    return entries.filter(isEntry);
  } catch {
    return [];
  }
}

export function saveHistory(entries: HistoryEntry[]): boolean {
  try {
    localStorage.setItem(KEY, JSON.stringify({ version: 1, entries }));
    return true;
  } catch {
    return false;
  }
}

export function historyFile(entries: HistoryEntry[]) {
  return { version: 1, entries };
}

export function entriesFromImport(parsed: unknown): HistoryEntry[] | null {
  if (Array.isArray(parsed)) {
    const entries = parsed.filter(isEntry);
    return entries.length ? entries : null;
  }
  if (parsed && typeof parsed === "object" && Array.isArray((parsed as { entries?: unknown }).entries)) {
    const entries = (parsed as { entries: unknown[] }).entries.filter(isEntry);
    return entries.length ? entries : null;
  }
  return null;
}
