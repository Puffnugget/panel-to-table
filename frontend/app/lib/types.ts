export type Sex = "female" | "male";
export type Tier = "in_range" | "borderline" | "out_of_range" | "see_doctor" | "unrated";

export type MarkerInput = {
  id: string;
  value: number;
  unit: string;
  lab_low?: number | null;
  lab_high?: number | null;
};

export type AnalyzeRequest = {
  age: number;
  sex: Sex;
  test_date: string;
  fasting: boolean;
  markers: MarkerInput[];
  name?: string;
};

export type RangeBarData = {
  min: number;
  max: number;
  value: number;
  zones: { start: number; end: number; tier: Tier }[];
  band_low: number;
  band_high: number;
};

export type MarkerResult = {
  id: string;
  name: string;
  value: number;
  unit: string;
  entered_value: number;
  entered_unit: string;
  tier: Tier;
  direction: "high" | "low" | null;
  message: string;
  foods: string[];
  tip: string | null;
  bar: RangeBarData;
};

export type Recipe = {
  title: string;
  url: string;
  tags: string[];
  source: string;
  image?: string | null;
};

export type MealOption = {
  why: string;
  recipe: Recipe;
};

export type MealSlot = {
  slot: string;
  label: string;
  options: MealOption[];
};

export type MealPlan = {
  summary: string;
  day: MealSlot[];
};

export type AnalyzeResponse = {
  see_doctor: string[];
  results: MarkerResult[];
  focus: string[];
  activity: string;
  recipes: Recipe[];
  meals?: MealPlan;
};

export type HistoryEntry = {
  id: string;
  savedAt: string;
  request: AnalyzeRequest;
  response: AnalyzeResponse;
};

export type MarkerDraft = {
  value: string;
  unit: string;
  labLow: string;
  labHigh: string;
};

export type FormState = {
  age: string;
  sex: "" | Sex;
  testDate: string;
  fasting: "" | "yes" | "no";
  markers: Record<string, MarkerDraft>;
};

export type PdfCandidate = {
  id: string;
  name: string;
  value: number;
  unit: string;
  unit_found: boolean;
  lab_low: number | null;
  lab_high: number | null;
  source_line: string;
};

export type ParseResponse = {
  ok: boolean;
  message: string;
  candidates: PdfCandidate[];
  missing: string[];
};

export const TIER_LABEL: Record<Tier, string> = {
  in_range: "In range",
  borderline: "Borderline",
  out_of_range: "Outside range",
  see_doctor: "See a doctor",
  unrated: "No status",
};

export const FOCUS_LABEL: Record<string, string> = {
  heart: "Heart",
  blood_sugar: "Blood sugar",
  iron_b12: "Iron and B12",
  vitamin_d: "Vitamin D",
  balanced: "Balanced",
};
