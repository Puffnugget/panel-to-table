import type { MarkerResult } from "../lib/types";

export function DoctorCallout({ results }: { results: MarkerResult[] }) {
  const flagged = results.filter((result) => result.tier === "see_doctor");
  if (!flagged.length) return null;
  return (
    <section className="doctor-callout" role="alert">
      <h2 className="text-2xl font-semibold">See a doctor before changing food for these</h2>
      <ul className="mt-3 space-y-2">
        {flagged.map((result) => (
          <li key={result.id}><span className="font-semibold">{result.name}.</span> {result.message}</li>
        ))}
      </ul>
      <p className="mt-3 text-sm">
        If you feel sick right now, contact a clinician or urgent care. This page is not an emergency service, and it will not suggest meals for the markers above.
      </p>
    </section>
  );
}
