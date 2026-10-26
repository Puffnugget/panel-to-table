"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Disclaimer } from "../components/Disclaimer";
import { ExportSection } from "../components/ExportSection";
import { HistoryList } from "../components/HistoryList";
import { MarkerForm } from "../components/MarkerForm";
import { ResultsPanel } from "../components/ResultsPanel";
import { SiteHeader } from "../components/SiteHeader";
import { analyze, parseReport } from "../lib/api";
import { buildRequest } from "../lib/form";
import { entriesFromImport, loadHistory, saveHistory } from "../lib/history";
import { emptyForm } from "../lib/markers";
import { SAMPLES, formFromRequest } from "../lib/sampleData";
import type { AnalyzeRequest, FormState, HistoryEntry, PdfCandidate } from "../lib/types";

function newId() {
  return globalThis.crypto?.randomUUID?.() ?? `test-${Date.now()}`;
}

function errorText(error: unknown) {
  return error instanceof Error ? error.message : "Something went wrong.";
}

export default function TestInputPage() {
  const [form, setForm] = useState<FormState>(emptyForm);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const historyRef = useRef<HistoryEntry[]>([]);
  const [current, setCurrent] = useState<HistoryEntry | null>(null);
  const [busy, setBusy] = useState<null | "analyze" | "pdf">(null);
  const [error, setError] = useState<string | null>(null);
  const [pdfNote, setPdfNote] = useState<string | null>(null);
  const [review, setReview] = useState<PdfCandidate[]>([]);
  const [storageOk, setStorageOk] = useState(true);

  useEffect(() => {
    const loaded = loadHistory();
    historyRef.current = loaded;
    setHistory(loaded);
  }, []);

  useEffect(() => {
    if (!current) return;
    document.getElementById("results")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [current]);

  function store(next: HistoryEntry[]) {
    historyRef.current = next;
    setHistory(next);
    setStorageOk(saveHistory(next));
  }

  async function runAnalyze(request: AnalyzeRequest) {
    setBusy("analyze");
    setError(null);
    try {
      const response = await analyze(request);
      const entry: HistoryEntry = {
        id: newId(),
        savedAt: new Date().toISOString(),
        request,
        response,
      };
      setCurrent(entry);
      store([...historyRef.current, entry]);
    } catch (err) {
      setError(errorText(err));
    } finally {
      setBusy(null);
    }
  }

  function onSubmit() {
    const built = buildRequest(form);
    if ("error" in built) {
      setError(built.error);
      return;
    }
    void runAnalyze(built.request);
  }

  function onSample(sampleId: string) {
    const sample = SAMPLES.find((item) => item.id === sampleId);
    if (!sample) return;
    setForm(formFromRequest(sample.request));
    setReview([]);
    setPdfNote(null);
    void runAnalyze(sample.request);
  }

  async function onPdf(file: File) {
    setBusy("pdf");
    setError(null);
    setPdfNote("Reading the PDF…");
    try {
      const parsed = await parseReport(file);
      if (!parsed.ok) {
        setReview([]);
        setPdfNote(parsed.message);
        return;
      }
      setForm((currentForm) => {
        const markers = { ...currentForm.markers };
        for (const candidate of parsed.candidates) {
          if (!markers[candidate.id]) continue;
          markers[candidate.id] = {
            value: String(candidate.value),
            unit: candidate.unit,
            labLow: candidate.lab_low == null ? "" : String(candidate.lab_low),
            labHigh: candidate.lab_high == null ? "" : String(candidate.lab_high),
          };
        }
        return { ...currentForm, markers };
      });
      setReview(parsed.candidates);
      const missingUnit = parsed.candidates.some((candidate) => candidate.unit_found === false);
      setPdfNote(
        missingUnit
          ? `${parsed.message} A unit was missing on at least one line. Please confirm the dropdowns.`
          : parsed.message,
      );
    } catch (err) {
      setReview([]);
      setPdfNote(errorText(err));
    } finally {
      setBusy(null);
    }
  }

  function onOpen(entry: HistoryEntry) {
    setCurrent(entry);
    setForm(formFromRequest(entry.request));
    setError(null);
  }

  function onRemove(id: string) {
    store(historyRef.current.filter((entry) => entry.id !== id));
  }

  async function onImport(file: File) {
    try {
      const incoming = entriesFromImport(JSON.parse(await file.text()));
      if (!incoming) {
        setError("This file isn’t a Panel to Table history export.");
        return;
      }
      const merged = new Map(historyRef.current.map((entry) => [entry.id, entry]));
      for (const entry of incoming) merged.set(entry.id, entry);
      store([...merged.values()]);
      setError(null);
    } catch {
      setError("This file isn’t a Panel to Table history export.");
    }
  }

  return (
    <div className="min-h-screen w-full p-6 sm:p-10">
      <div className="max-w-5xl mx-auto space-y-6">
        <SiteHeader />
        <Disclaimer />
        <MarkerForm
          form={form}
          onChange={setForm}
          onSubmit={onSubmit}
          onSample={onSample}
          onPdf={onPdf}
          busy={busy !== null}
          error={error}
        />
        {pdfNote && <p className="card p-4" role="status">{pdfNote}</p>}
        {review.length > 0 && (
          <section className="card p-5">
            <h2 className="text-2xl font-semibold">Check the numbers we read</h2>
            <p className="mt-1 text-sm text-gray-700">
              Nothing is analyzed until you click Analyze. Fix anything that looks wrong. The PDF itself is not saved.
            </p>
            <ul className="mt-3 space-y-1 text-sm">
              {review.map((line) => (
                <li key={line.id}><code>{line.source_line}</code></li>
              ))}
            </ul>
          </section>
        )}
        {busy === "analyze" && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" role="status">
            <div className="bg-white rounded-lg p-8 max-w-md mx-4 text-center">
              <div className="spinner mx-auto mb-4" />
              <h2 className="text-xl font-semibold">Comparing your numbers</h2>
              <p className="text-gray-600 mt-2">
                If this is the first visit in a while, the server may be waking up. That can take a few seconds.
              </p>
              <div className="bar-indeterminate mt-4"><span /></div>
            </div>
          </div>
        )}
        {current && <ResultsPanel response={current.response} />}
        {!storageOk && (
          <p className="text-sm text-alert" role="status">
            This browser blocked saving, so a refresh will clear the new result. You can still download JSON.
          </p>
        )}
        <ExportSection entries={history} current={current} onImport={onImport} />
        <section className="card p-5 space-y-4">
          <h2 className="text-2xl font-semibold">Saved tests</h2>
          <p className="text-sm text-gray-600">
            Kept in this browser only. Analyze sends the numbers you typed so they can be compared, and the server does not store them.
          </p>
          <HistoryList entries={history} activeId={current?.id ?? null} onOpen={onOpen} onRemove={onRemove} />
          <p className="text-sm">
            <Link className="text-link" href="/results">Open the results tab</Link> for every saved test and a graph of each marker over time.
          </p>
        </section>
      </div>
    </div>
  );
}
