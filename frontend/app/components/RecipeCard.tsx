import type { Recipe } from "../lib/types";

const TAG_LABEL: Record<string, string> = {
  fiber: "fiber",
  heart: "heart",
  unsaturated_fat: "olive oil or nuts",
  omega3: "omega-3",
  low_sugar: "fewer added sugars",
  blood_sugar: "blood sugar",
  whole_grain: "whole grain",
  vitamin_d: "vitamin D",
  vitamin_c: "vitamin C",
  iron: "iron",
  b12: "B12",
  fish: "fish",
  eggs: "eggs",
  vegetarian: "vegetarian",
  balanced: "everyday",
};

export function RecipeCard({ recipe }: { recipe: Recipe }) {
  return (
    <article className="p-4 border border-[var(--sun)] rounded-lg bg-[var(--sun-light)] flex flex-col gap-2">
      {recipe.image && (
        <img src={recipe.image} alt="" className="h-36 w-full rounded-lg object-cover" />
      )}
      <h3 className="text-lg font-semibold">{recipe.title}</h3>
      <p className="text-sm text-gray-600">{recipe.source}</p>
      <ul className="flex flex-wrap gap-1">
        {recipe.tags.map((tag) => (
          <li key={tag} className="bg-white border border-[var(--mint-light)] rounded-full px-2 py-0.5 text-xs">
            {TAG_LABEL[tag] || tag}
          </li>
        ))}
      </ul>
      <a className="btn mt-auto text-center" href={recipe.url} target="_blank" rel="noreferrer">
        Open recipe
      </a>
    </article>
  );
}
