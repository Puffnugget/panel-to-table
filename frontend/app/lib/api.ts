import type { AnalyzeRequest, AnalyzeResponse, MealPlan, ParseResponse } from "./types";

export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const WAKE =
  "The server may be waking up. Wait a few seconds and try again.";

async function readError(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail
        .map((item: { msg?: string }) => item?.msg || "Check the form and try again.")
        .join(" ");
    }
  } catch {
    /* The body was not JSON. */
  }
  return `Request failed (${response.status}).`;
}

async function post(path: string, init: RequestInit): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 45000);
  try {
    return await fetch(`${API_URL}${path}`, { ...init, signal: controller.signal });
  } catch {
    throw new Error(WAKE);
  } finally {
    clearTimeout(timer);
  }
}

export async function analyze(request: AnalyzeRequest): Promise<AnalyzeResponse> {
  const response = await post("/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}

export type FoodStat = {
  id: string;
  label: string;
  unit: string;
  per_100g: number | null;
  per_serving: number | null;
};

export type FoodMatch = {
  name: string;
  brand: string | null;
  barcode: string | null;
  serving: string | null;
  stats: FoodStat[];
  url: string | null;
};

export async function generateMealPlan(
  input: AnalyzeRequest & { diet?: string | null; intolerances: string[] },
): Promise<MealPlan> {
  const response = await post("/meal-plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!response.ok) throw new Error(await readError(response));
  const body = (await response.json()) as { meals: MealPlan };
  return body.meals;
}

export async function lookupFood(input: { barcode?: string; query?: string }): Promise<FoodMatch[]> {
  const response = await post("/food", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!response.ok) throw new Error(await readError(response));
  const body = (await response.json()) as { matches: FoodMatch[] };
  return body.matches;
}

export async function parseReport(file: File): Promise<ParseResponse> {
  const form = new FormData();
  form.append("file", file);
  const response = await post("/parse-report", { method: "POST", body: form });
  if (!response.ok) throw new Error(await readError(response));
  return response.json();
}
