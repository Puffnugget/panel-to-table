"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useState } from "react";
import { Disclaimer } from "../components/Disclaimer";
import { HistoryList } from "../components/HistoryList";
import { ResultsPanel } from "../components/ResultsPanel";
import { SiteHeader } from "../components/SiteHeader";
import { loadHistory, saveHistory } from "../lib/history";
import { MARKERS } from "../lib/markers";
import type { HistoryEntry } from "../lib/types";

const MarkerTrendChart = dynamic(() => import("../components/MarkerTrendChart"), {
  ssr: false,
  loading: () => <p className="text-sm text-gray-600">Loading chart…</p>,
});

export default function ResultsPage() {
  const [entries, setEntries] = useState<HistoryEntry[]>([]);
  const [openId, setOpenId] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    setEntries(loadHistory());
    setReady(true);
  }, []);

  const personOf = (entry: HistoryEntry) => entry.request.name?.trim() || "";
  const people = [...new Set(entries.map(personOf))];
  const [pickedPerson, setPickedPerson] = useState<string | null>(null);
  const person = pickedPerson ?? (people.includes("Maya") ? "Maya" : people[0] ?? "");
  const graphed = entries.filter((entry) => personOf(entry) === person);
  const open = entries.find((entry) => entry.id === openId) ?? null;
  const plotted = MARKERS.filter((marker) =>
    graphed.some((entry) => entry.response.results.some((result) => result.id === marker.id)),
  );
  const missing = MARKERS.filter((marker) => !plotted.some((item) => item.id === marker.id));

  function remove(id: string) {
    const next = entries.filter((entry) => entry.id !== id);
    setEntries(next);
    if (openId === id) setOpenId(null);
    saveHistory(next);
  }

  return (
    <div className="min-h-screen w-full p-6 sm:p-10">
      <div className="max-w-5xl mx-auto space-y-6">
        <SiteHeader />
        <Disclaimer />
        <section className="card p-5 space-y-4">
          <h2 className="text-2xl font-semibold">All test results</h2>
          <p className="text-sm text-gray-600">
            Every test saved in this browser. Each marker gets its own graph so a change over time is easy to see. The shaded band is the usual range from the latest test that included that marker.
          </p>
          {!ready ? (
            <p>Loading saved tests…</p>
          ) : entries.length === 0 ? (
            <p>
              No saved tests yet. <Link className="text-link" href="/test">Enter a result or try a sample</Link> and it will show up here.
            </p>
          ) : (
            <HistoryList
              entries={entries}
              activeId={openId}
              onOpen={(entry) => setOpenId(entry.id === openId ? null : entry.id)}
              onRemove={remove}
            />
          )}
        </section>
        {open && <ResultsPanel response={open.response} />}
        {people.length > 1 && (
          <label className="block text-sm font-medium">
            Whose tests to graph
            <select className="field mt-1" value={person} onChange={(event) => setPickedPerson(event.target.value)}>
              {people.map((name) => (
                <option key={name || "other"} value={name}>{name || "Other saved tests"}</option>
              ))}
            </select>
          </label>
        )}
        {plotted.length > 0 && (
          <div className="grid gap-4 lg:grid-cols-2">
            {plotted.map((marker) => (
              <section key={marker.id} className="card p-5">
                <h2 className="text-xl font-semibold">{marker.name}</h2>
                <MarkerTrendChart entries={graphed} markerId={marker.id} />
              </section>
            ))}
          </div>
        )}
        {ready && graphed.length > 0 && missing.length > 0 && (
          <p className="text-sm text-gray-600">
            No saved points yet for {missing.map((marker) => marker.name).join(", ")}.
          </p>
        )}
      </div>
    </div>
  );
}
