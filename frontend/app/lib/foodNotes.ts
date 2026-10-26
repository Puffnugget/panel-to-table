import type { FoodStat } from "./api";
import type { HistoryEntry, MarkerResult } from "./types";

function stat(stats: FoodStat[], id: string) {
  return stats.find((item) => item.id === id)?.per_100g ?? null;
}

function flagged(results: MarkerResult[], id: string, direction: "high" | "low") {
  const item = results.find((result) => result.id === id);
  if (!item) return false;
  if (item.tier !== "borderline" && item.tier !== "out_of_range") return false;
  return item.direction === direction;
}

export function foodNotes(stats: FoodStat[], latest: HistoryEntry | null): string[] {
  if (!latest) return [];
  const results = latest.response.results;
  const notes: string[] = [];
  const fiber = stat(stats, "fiber");
  const sugars = stat(stats, "sugars");
  const saturated = stat(stats, "saturated-fat");
  const iron = stat(stats, "iron");
  const vitaminD = stat(stats, "vitamin-d");

  if (fiber != null && fiber >= 6 && flagged(results, "ldl", "high")) {
    notes.push("This label is high in fiber. Fiber-rich foods were one of the ideas for your latest LDL result.");
  }
  if (sugars != null && sugars >= 15 && (flagged(results, "glucose", "high") || flagged(results, "a1c", "high"))) {
    notes.push("Sugars are high on this label. Your latest blood sugar marker was outside the usual range.");
  }
  if (saturated != null && saturated >= 5 && flagged(results, "ldl", "high")) {
    notes.push("Saturated fat is fairly high on this label, and your latest LDL was outside the usual range.");
  }
  if (iron != null && iron >= 2 && flagged(results, "ferritin", "low")) {
    notes.push("This food lists iron. Your latest ferritin was on the low side.");
  }
  if (vitaminD != null && vitaminD > 0 && flagged(results, "vitamin_d", "low")) {
    notes.push("This food lists vitamin D. Your latest vitamin D was on the low side. Supplements still belong with a doctor.");
  }
  return notes;
}
