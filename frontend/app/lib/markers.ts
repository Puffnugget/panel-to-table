import type { FormState, MarkerDraft } from "./types";

export const MARKERS = [
  { id: "ldl", name: "LDL cholesterol", units: ["mg/dL", "mmol/L"], hint: "The “bad” cholesterol number on a lipid panel." },
  { id: "hdl", name: "HDL cholesterol", units: ["mg/dL", "mmol/L"], hint: "Higher is the usual direction for HDL." },
  { id: "triglycerides", name: "Triglycerides", units: ["mg/dL", "mmol/L"], hint: "Status is skipped if this was not a fasting test." },
  { id: "glucose", name: "Fasting glucose", units: ["mg/dL", "mmol/L"], hint: "Status is skipped if this was not a fasting test." },
  { id: "a1c", name: "Hemoglobin A1c", units: ["%", "mmol/mol"], hint: "A longer look at blood sugar, not a single meal." },
  { id: "vitamin_d", name: "Vitamin D (25-hydroxy)", units: ["ng/mL", "nmol/L"], hint: "High vitamin D does not get more vitamin D foods." },
  { id: "ferritin", name: "Ferritin", units: ["ng/mL", "mcg/L"], hint: "Add the range printed on the report when you have it." },
  { id: "b12", name: "Vitamin B12", units: ["pg/mL", "pmol/L"], hint: "Marginal is 200–299 pg/mL." },
] as const;

export function emptyDraft(unit: string): MarkerDraft {
  return { value: "", unit, labLow: "", labHigh: "" };
}

export function emptyForm(): FormState {
  return {
    age: "",
    sex: "",
    testDate: "",
    fasting: "",
    markers: Object.fromEntries(MARKERS.map((marker) => [marker.id, emptyDraft(marker.units[0])])),
  };
}
