import type { AnalyzeRequest } from "./types";
import { emptyForm } from "./markers";
import type { FormState } from "./types";

export type SampleProfile = {
  id: string;
  label: string;
  detail: string;
  request: AnalyzeRequest;
};

export const SAMPLES: SampleProfile[] = [
  {
    id: "in-range",
    label: "All in range",
    detail: "Adult, fasting, every marker in the usual range.",
    request: {
      age: 34,
      sex: "male",
      test_date: "2026-06-01",
      fasting: true,
      markers: [
        { id: "ldl", value: 90, unit: "mg/dL" },
        { id: "hdl", value: 55, unit: "mg/dL" },
        { id: "triglycerides", value: 100, unit: "mg/dL" },
        { id: "glucose", value: 88, unit: "mg/dL" },
        { id: "a1c", value: 5.3, unit: "%" },
        { id: "vitamin_d", value: 32, unit: "ng/mL" },
        { id: "ferritin", value: 80, unit: "ng/mL", lab_low: 30, lab_high: 400 },
        { id: "b12", value: 500, unit: "pg/mL" },
      ],
    },
  },
  {
    id: "mixed",
    label: "Mixed results",
    detail: "Age 16 and fasting, with borderline lipids, low vitamin D, and low ferritin.",
    request: {
      age: 16,
      sex: "female",
      test_date: "2026-09-14",
      fasting: true,
      markers: [
        { id: "ldl", value: 118, unit: "mg/dL" },
        { id: "hdl", value: 42, unit: "mg/dL" },
        { id: "triglycerides", value: 95, unit: "mg/dL" },
        { id: "glucose", value: 96, unit: "mg/dL" },
        { id: "a1c", value: 5.5, unit: "%" },
        { id: "vitamin_d", value: 18, unit: "ng/mL" },
        { id: "ferritin", value: 9, unit: "ng/mL", lab_low: 13, lab_high: 150 },
        { id: "b12", value: 240, unit: "pg/mL" },
      ],
    },
  },
  {
    id: "doctor",
    label: "Needs a doctor",
    detail: "Several markers cross the see-a-doctor line. Food tips turn off for those.",
    request: {
      age: 52,
      sex: "female",
      test_date: "2026-10-01",
      fasting: true,
      markers: [
        { id: "ldl", value: 198, unit: "mg/dL" },
        { id: "hdl", value: 38, unit: "mg/dL" },
        { id: "triglycerides", value: 210, unit: "mg/dL" },
        { id: "glucose", value: 130, unit: "mg/dL" },
        { id: "a1c", value: 6.6, unit: "%" },
        { id: "vitamin_d", value: 62, unit: "ng/mL" },
        { id: "ferritin", value: 400, unit: "ng/mL", lab_low: 15, lab_high: 150 },
        { id: "b12", value: 180, unit: "pg/mL" },
      ],
    },
  },
];

export function formFromRequest(request: AnalyzeRequest): FormState {
  const form = emptyForm();
  form.age = String(request.age);
  form.sex = request.sex;
  form.testDate = request.test_date;
  form.fasting = request.fasting ? "yes" : "no";
  for (const marker of request.markers) {
    form.markers[marker.id] = {
      value: String(marker.value),
      unit: marker.unit,
      labLow: marker.lab_low == null ? "" : String(marker.lab_low),
      labHigh: marker.lab_high == null ? "" : String(marker.lab_high),
    };
  }
  return form;
}
