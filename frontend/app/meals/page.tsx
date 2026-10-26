"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { Disclaimer } from "../components/Disclaimer";
import { MealDay } from "../components/MealDay";
import { SiteHeader } from "../components/SiteHeader";
import { generateMealPlan } from "../lib/api";
import { loadHistory } from "../lib/history";
import type { HistoryEntry, MealPlan } from "../lib/types";

const PREFS_KEY = "panel-to-table.meal-prefs.v1";

const DIETS = [
  { id: "", label: "No specific diet" },
  { id: "gluten free", label: "Gluten free" },
  { id: "ketogenic", label: "Ketogenic" },
  { id: "vegetarian", label: "Vegetarian" },
  { id: "lacto-vegetarian", label: "Lacto-vegetarian" },
  { id: "ovo-vegetarian", label: "Ovo-vegetarian" },
  { id: "vegan", label: "Vegan" },
  { id: "pescetarian", label: "Pescetarian" },
  { id: "paleo", label: "Paleo" },
  { id: "primal", label: "Primal" },
  { id: "low fodmap", label: "Low FODMAP" },
  { id: "whole30", label: "Whole30" },
];

const INTOLERANCES = [
  ["dairy", "Dairy"],
  ["egg", "Egg"],
  ["gluten", "Gluten"],
  ["grain", "Grain"],
  ["peanut", "Peanut"],
  ["seafood", "Seafood"],
  ["sesame", "Sesame"],
  ["shellfish", "Shellfish"],
  ["soy", "Soy"],
  ["sulfite", "Sulfite"],
  ["tree nut", "Tree nut"],
  ["wheat", "Wheat"],
] as const;

function Planner() {
  const params = useSearchParams();
  const requested = params.get("test");
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [pickedId, setPickedId] = useState<string | null>(requested);
  const [diet, setDiet] = useState("");
  const [intolerances, setIntolerances] = useState<string[]>([]);
  const [plan, setPlan] = useState<MealPlan | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const loaded = loadHistory().sort((a, b) => b.request.test_date.localeCompare(a.request.test_date));
    setEntries(loaded);
    setPickedId((current) => current && loaded.some((entry) => entry.id === current) ? current : loaded[0]?.id ?? null);
    try {
      const saved = JSON.parse(localStorage.getItem(PREFS_KEY) || "null") as { diet?: string; intolerances?: string[] } | null;
      const allowed = new Set(INTOLERANCES.map(([id]) => id));
      if (saved && DIETS.some((item) => item.id === saved.diet)) setDiet(saved.diet || "");
      if (saved && Array.isArray(saved.intolerances)) {
        setIntolerances(saved.intolerances.filter((item) => allowed.has(item as (typeof INTOLERANCES)[number][0])));
      }
    } catch {
      /* A bad saved preference just starts from the blank form. */
    }
    setReady(true);
  }, []);

  useEffect(() => {
    if (!ready) return;
    localStorage.setItem(PREFS_KEY, JSON.stringify({ diet, intolerances }));
  }, [diet, intolerances, ready]);

  const entry = entries.find((item) => item.id === pickedId) ?? null;

  function toggleIntolerance(id: string) {
    setIntolerances((current) => (current.includes(id) ? current.filter((item) => item !== id) : [...current, id]));
  }

  async function generate() {
    if (!entry) return;
    setLoading(true);
    setError(null);
    try {
      const next = await generateMealPlan({
        ...entry.request,
        diet: diet || null,
        intolerances,
      });
      setPlan(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen w-full p-6 sm:p-10">
      <div className="max-w-5xl mx-auto space-y-6">
        <SiteHeader />
        <Disclaimer />
        <section className="card p-5 space-y-4">
          <h2 className="text-2xl font-semibold">A day of meals</h2>
          <p>
            Spoonacular builds breakfast, lunch, and dinner from the saved test you pick. Choose a diet and any allergies first. Generate again whenever you want a different day.
          </p>
          <p className="text-sm text-gray-600">
            The test and the boxes below are sent to our server, which asks Spoonacular for recipes. The API key stays on the server. The plan is not stored.
          </p>
          {!ready ? (
            <p>Loading saved tests…</p>
          ) : entries.length === 0 ? (
            <p>
              No saved tests yet. <Link className="text-link" href="/test">Enter a result or try a sample</Link> and then generate a day here.
            </p>
          ) : (
            <>
              <label className="block text-sm font-medium">
                Which test
                <select
                  className="field mt-1"
                  value={pickedId ?? ""}
                  onChange={(event) => setPickedId(event.target.value)}
                >
                  {entries.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.request.name ? `${item.request.name} · ` : ""}{item.request.test_date} · age {item.request.age}
                    </option>
                  ))}
                </select>
              </label>
              <label className="block text-sm font-medium">
                Diet
                <select className="field mt-1" value={diet} onChange={(event) => setDiet(event.target.value)}>
                  {DIETS.map((item) => (
                    <option key={item.id || "none"} value={item.id}>{item.label}</option>
                  ))}
                </select>
              </label>
              <fieldset>
                <legend className="text-sm font-medium">Allergies and ingredients to leave out</legend>
                <div className="mt-2 flex flex-wrap gap-2">
                  {INTOLERANCES.map(([id, label]) => (
                    <label key={id} className="flex items-center gap-2 rounded-full border border-[var(--sun)] bg-white px-3 py-1 text-sm">
                      <input
                        type="checkbox"
                        checked={intolerances.includes(id)}
                        onChange={() => toggleIntolerance(id)}
                      />
                      {label}
                    </label>
                  ))}
                </div>
              </fieldset>
              <button className="btn" type="button" onClick={() => void generate()} disabled={loading || !entry}>
                {loading ? "Asking Spoonacular…" : plan ? "Generate another day" : "Generate a day"}
              </button>
            </>
          )}
          {error && <p className="text-alert" role="alert">{error}</p>}
        </section>
        {plan && (
          <section className="card p-5">
            <MealDay key={plan.day.map((slot) => slot.options[0]?.recipe.url).join("|")} plan={plan} />
          </section>
        )}
      </div>
    </div>
  );
}

export default function MealsPage() {
  return (
    <Suspense fallback={<p className="p-6">Loading meals…</p>}>
      <Planner />
    </Suspense>
  );
}
