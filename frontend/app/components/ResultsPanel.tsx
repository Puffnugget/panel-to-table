import Link from "next/link";
import { FOCUS_LABEL, type AnalyzeResponse } from "../lib/types";
import { DoctorCallout } from "./DoctorCallout";
import { MarkerCard } from "./MarkerCard";
import { MealDay } from "./MealDay";
import { RecipeCard } from "./RecipeCard";

export function ResultsPanel({ response }: { response: AnalyzeResponse }) {
  const balanced = response.focus.length === 1 && response.focus[0] === "balanced";
  return (
    <div id="results" className="space-y-6">
      <DoctorCallout results={response.results} />

      <section className="card p-5">
        <h2 className="text-2xl font-semibold">Food focus</h2>
        <ul className="mt-3 flex flex-wrap gap-2">
          {response.focus.map((focus) => (
            <li key={focus} className="bg-[var(--sun)] rounded-full px-3 py-1 text-sm">{FOCUS_LABEL[focus] || focus}</li>
          ))}
        </ul>
        <p className="mt-3 text-sm text-gray-700">
          {balanced
            ? "Nothing entered was outside the usual range, so the meals below are everyday ideas rather than a fix for one marker."
            : "These themes follow markers that are borderline or outside the usual range. Markers that need a doctor do not add a food theme."}
        </p>
      </section>

      <section className="card p-5 space-y-4">
        <h2 className="text-2xl font-semibold">Each marker</h2>
        {response.results.map((result) => (
          <MarkerCard key={result.id} result={result} />
        ))}
      </section>

      <section className="card p-5">
        <h2 className="text-2xl font-semibold">Activity</h2>
        <p className="mt-2">{response.activity}</p>
      </section>

      <section className="card p-5">
        <h2 className="text-2xl font-semibold">A day of meals</h2>
        <p className="mt-2 text-sm text-gray-700">
          From the American Heart Association and Cleveland Clinic. Iron-focused recipes are left out when ferritin is high, and vitamin D recipes are left out when vitamin D is high.
        </p>
        {response.meals ? (
          <div className="mt-4">
            <MealDay plan={response.meals} />
          </div>
        ) : (
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {response.recipes.map((recipe) => (
              <RecipeCard key={recipe.url} recipe={recipe} />
            ))}
          </div>
        )}
        <p className="mt-4 text-sm">
          <Link className="text-link" href="/meals">Open the Meals tab</Link> to generate a new day from Spoonacular, with a diet or allergies.
        </p>
      </section>
    </div>
  );
}
