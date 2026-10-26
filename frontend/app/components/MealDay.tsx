"use client";

import { useState } from "react";
import type { MealPlan } from "../lib/types";
import { RecipeCard } from "./RecipeCard";

export function MealDay({ plan }: { plan: MealPlan }) {
  const [picked, setPicked] = useState<Record<string, number>>({});
  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-700">{plan.summary}</p>
      <div className="grid gap-4 lg:grid-cols-3">
        {plan.day.map((slot) => {
          const options = slot.options.length ? slot.options : [];
          const index = options.length ? (picked[slot.slot] || 0) % options.length : 0;
          const option = options[index];
          if (!option) return null;
          return (
            <div key={slot.slot} className="space-y-2">
              <h3 className="text-xl font-semibold">{slot.label}</h3>
              <RecipeCard recipe={option.recipe} />
              <p className="text-sm">{option.why}</p>
              {options.length > 1 && (
                <button
                  className="btn btn-secondary"
                  type="button"
                  onClick={() => setPicked((current) => ({ ...current, [slot.slot]: index + 1 }))}
                >
                  Swap this meal
                </button>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
