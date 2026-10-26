import { TIER_LABEL, type MarkerResult } from "../lib/types";
import { RangeBar } from "./RangeBar";

const TONE: Record<MarkerResult["tier"], string> = {
  in_range: "tone-in_range",
  borderline: "tone-borderline",
  out_of_range: "tone-out_of_range",
  see_doctor: "tone-see_doctor",
  unrated: "tone-unrated",
};

export function MarkerCard({ result }: { result: MarkerResult }) {
  const converted = result.entered_unit !== result.unit;
  const barLabel = `${result.name} ${result.value} ${result.unit}, ${TIER_LABEL[result.tier]}. Usual span ${result.bar.band_low} to ${result.bar.band_high}.`;
  return (
    <article className={`p-4 rounded-lg border-l-4 ${TONE[result.tier]}`}>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-lg font-semibold">{result.name}</h3>
        <span className="bg-white px-2 py-1 rounded-full text-xs font-medium">{TIER_LABEL[result.tier]}</span>
      </div>
      <p className="mt-1 text-sm">
        <span className="font-medium">{result.value} {result.unit}</span>
        {converted && (
          <span className="text-gray-600"> (entered {result.entered_value} {result.entered_unit})</span>
        )}
      </p>
      {result.tier !== "unrated" && <RangeBar bar={result.bar} label={barLabel} />}
      <p className="mt-3 text-sm">{result.message}</p>
      {result.foods.length > 0 && (
        <p className="mt-2 text-sm"><span className="font-medium">Foods to consider: </span>{result.foods.join(", ")}</p>
      )}
      {result.tip && <p className="mt-1 text-sm">{result.tip}</p>}
    </article>
  );
}
