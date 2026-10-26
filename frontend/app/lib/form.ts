import { MARKERS } from "./markers";
import type { AnalyzeRequest, FormState, MarkerInput } from "./types";

function numberOrNull(raw: string): number | null | "bad" {
  const text = raw.trim();
  if (!text) return null;
  const value = Number(text);
  if (!Number.isFinite(value)) return "bad";
  return value;
}

export function buildRequest(form: FormState): { request: AnalyzeRequest } | { error: string } {
  const age = Number(form.age);
  if (!form.age.trim() || !Number.isInteger(age) || age < 1 || age > 120) {
    return { error: "Enter an age from 1 to 120." };
  }
  if (form.sex !== "female" && form.sex !== "male") {
    return { error: "Choose female or male. HDL ranges use that answer for adults." };
  }
  if (!form.testDate) {
    return { error: "Enter the date of the test." };
  }
  if (form.fasting !== "yes" && form.fasting !== "no") {
    return { error: "Say whether this was a fasting test." };
  }

  const markers: MarkerInput[] = [];
  for (const marker of MARKERS) {
    const draft = form.markers[marker.id];
    const value = numberOrNull(draft?.value ?? "");
    const labLow = numberOrNull(draft?.labLow ?? "");
    const labHigh = numberOrNull(draft?.labHigh ?? "");
    if (value === "bad" || labLow === "bad" || labHigh === "bad") {
      return { error: `${marker.name} needs a plain number.` };
    }
    if (value === null && (labLow !== null || labHigh !== null)) {
      return { error: `Enter a value for ${marker.name}, or clear the lab range.` };
    }
    if (value === null) continue;
    if (labLow !== null && labHigh !== null && labLow > labHigh) {
      return { error: `${marker.name} has a lab range that runs backwards.` };
    }
    markers.push({
      id: marker.id,
      value,
      unit: draft.unit,
      lab_low: labLow,
      lab_high: labHigh,
    });
  }
  if (!markers.length) {
    return { error: "Enter at least one marker." };
  }
  return {
    request: {
      age,
      sex: form.sex,
      test_date: form.testDate,
      fasting: form.fasting === "yes",
      markers,
    },
  };
}
