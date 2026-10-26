"use client";

import { useCallback, useEffect, useState } from "react";
import { Disclaimer } from "../components/Disclaimer";
import { FoodScanner } from "../components/FoodScanner";
import { SiteHeader } from "../components/SiteHeader";
import { lookupFood, type FoodMatch } from "../lib/api";
import { foodNotes } from "../lib/foodNotes";
import { loadHistory } from "../lib/history";
import type { HistoryEntry } from "../lib/types";

function formatStat(value: number | null) {
  return value == null ? "—" : String(value);
}

export default function FoodPage() {
  const [barcode, setBarcode] = useState("");
  const [query, setQuery] = useState("");
  const [matches, setMatches] = useState<FoodMatch[]>([]);
  const [picked, setPicked] = useState(0);
  const [latest, setLatest] = useState<HistoryEntry | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const history = loadHistory();
    const sorted = [...history].sort((a, b) => b.request.test_date.localeCompare(a.request.test_date));
    setLatest(sorted[0] ?? null);
  }, []);

  const search = useCallback(async (input: { barcode?: string; query?: string }) => {
    setLoading(true);
    setError(null);
    try {
      const found = await lookupFood(input);
      setMatches(found);
      setPicked(0);
    } catch (err) {
      setMatches([]);
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }, []);

  const onCode = useCallback((code: string) => {
    const digits = code.replace(/\s/g, "");
    setBarcode(digits);
    void search({ barcode: digits });
  }, [search]);

  const onScanError = useCallback((message: string) => setError(message), []);
  const food = matches[picked];
  const notes = food ? foodNotes(food.stats, latest) : [];
  const hasServing = Boolean(food?.stats.some((item) => item.per_serving != null));

  return (
    <div className="min-h-screen w-full p-6 sm:p-10">
      <div className="max-w-3xl mx-auto space-y-6">
        <SiteHeader />
        <Disclaimer />
        <section className="card p-5 space-y-4">
          <h2 className="text-2xl font-semibold">Scan a food</h2>
          <p>
            Point the camera at a package barcode, or type a name. The numbers below are the nutrition label: calories, fiber, sugar, and the rest. They are not a judgment of the food.
          </p>
          <p className="text-sm text-gray-600">
            The barcode or name is sent to Open Food Facts, a public food database. Panel to Table does not store it.
          </p>
          <FoodScanner onCode={onCode} onError={onScanError} />
          <form
            className="flex flex-col gap-2 sm:flex-row sm:items-end"
            onSubmit={(event) => {
              event.preventDefault();
              void search({ barcode: barcode.trim() });
            }}
          >
            <label className="text-sm font-medium flex-1">
              Barcode
              <input className="field mt-1" inputMode="numeric" value={barcode} onChange={(event) => setBarcode(event.target.value)} placeholder="Digits under the bars" />
            </label>
            <button className="btn" type="submit" disabled={loading || !barcode.trim()}>
              {loading ? "Looking up…" : "Look up barcode"}
            </button>
          </form>
          <form
            className="flex flex-col gap-2 sm:flex-row sm:items-end"
            onSubmit={(event) => {
              event.preventDefault();
              void search({ query: query.trim() });
            }}
          >
            <label className="text-sm font-medium flex-1">
              Or search by name
              <input className="field mt-1" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Rolled oats" />
            </label>
            <button className="btn btn-secondary" type="submit" disabled={loading || query.trim().length < 2}>
              Search by name
            </button>
          </form>
          {error && <p className="text-sm text-alert" role="alert">{error}</p>}
        </section>

        {matches.length > 1 && (
          <section className="card p-5">
            <h2 className="text-xl font-semibold">Which package?</h2>
            <ul className="mt-3 space-y-2">
              {matches.map((match, index) => (
                <li key={`${match.barcode ?? match.name}-${index}`}>
                  <button className="btn btn-secondary w-full text-left" type="button" onClick={() => setPicked(index)} aria-current={index === picked ? "true" : undefined}>
                    {match.name}{match.brand ? ` · ${match.brand}` : ""}
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )}

        {food && (
          <section className="card p-5 space-y-3">
            <h2 className="text-2xl font-semibold">{food.name}</h2>
            <p className="text-sm text-gray-600">
              {food.brand ? `${food.brand}. ` : ""}
              {food.barcode ? `Barcode ${food.barcode}. ` : ""}
              {food.serving ? `Serving size ${food.serving}.` : "No serving size was printed in the database."}
            </p>
            {food.stats.length === 0 ? (
              <p>This product was found, but it has no nutrition numbers.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left border-b border-[var(--mint-light)]">
                      <th className="py-2 pr-3">Nutrient</th>
                      <th className="py-2 pr-3">Per 100 g</th>
                      {hasServing && <th className="py-2">Per serving</th>}
                    </tr>
                  </thead>
                  <tbody>
                    {food.stats.map((item) => (
                      <tr key={item.id} className="border-b border-[var(--mint-light)]">
                        <th className="py-2 pr-3 font-medium text-left">{item.label}</th>
                        <td className="py-2 pr-3">{formatStat(item.per_100g)} {item.unit}</td>
                        {hasServing && <td className="py-2">{formatStat(item.per_serving)} {item.per_serving == null ? "" : item.unit}</td>}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {notes.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold">Next to your latest test</h3>
                <ul className="mt-2 list-disc pl-5 space-y-1">
                  {notes.map((note) => <li key={note}>{note}</li>)}
                </ul>
                <p className="mt-2 text-sm text-gray-600">Markers that need a doctor are left out of these notes.</p>
              </div>
            )}
            {!latest && <p className="text-sm text-gray-600">Save a blood test on the Test Input page if you want these numbers set next to a result. The label stands on its own either way.</p>}
            {food.url && (
              <a className="text-link" href={food.url} target="_blank" rel="noreferrer">Open this product on Open Food Facts</a>
            )}
          </section>
        )}
      </div>
    </div>
  );
}
