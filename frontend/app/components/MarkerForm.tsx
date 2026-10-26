import { MARKERS } from "../lib/markers";
import { SAMPLES } from "../lib/sampleData";
import type { FormState } from "../lib/types";

type MarkerFormProps = {
  form: FormState;
  onChange: (form: FormState) => void;
  onSubmit: () => void;
  onSample: (sampleId: string) => void;
  onPdf: (file: File) => void;
  busy: boolean;
  error: string | null;
};

export function MarkerForm({ form, onChange, onSubmit, onSample, onPdf, busy, error }: MarkerFormProps) {
  const patch = (partial: Partial<FormState>) => onChange({ ...form, ...partial });
  const patchMarker = (id: string, partial: Partial<FormState["markers"][string]>) => {
    onChange({
      ...form,
      markers: { ...form.markers, [id]: { ...form.markers[id], ...partial } },
    });
  };

  return (
    <form
      className="card p-5 space-y-5"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <div>
        <h2 className="text-2xl font-semibold">Test Input</h2>
        <p className="mt-1 text-gray-700">
          Eight common markers. Leave a row blank if the report doesn’t include it. Results stay in this browser and are not saved on the server.
        </p>
      </div>

      {error && <p className="text-alert" role="alert">{error}</p>}

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="block text-sm font-medium">
          Age
          <input className="field mt-1" inputMode="numeric" value={form.age} onChange={(event) => patch({ age: event.target.value })} />
        </label>
        <label className="block text-sm font-medium">
          Test date
          <input className="field mt-1" type="date" value={form.testDate} onChange={(event) => patch({ testDate: event.target.value })} />
        </label>
      </div>

      <fieldset>
        <legend className="text-sm font-medium">Sex</legend>
        <p className="text-sm text-gray-600">Adult HDL uses different cut points for women and men. Under 20, the lipid ranges do not.</p>
        <div className="mt-2 flex gap-4">
          {(["female", "male"] as const).map((sex) => (
            <label key={sex} className="inline-flex items-center gap-2">
              <input type="radio" name="sex" checked={form.sex === sex} onChange={() => patch({ sex })} />
              {sex === "female" ? "Female" : "Male"}
            </label>
          ))}
        </div>
      </fieldset>

      <fieldset>
        <legend className="text-sm font-medium">Was this a fasting test?</legend>
        <p className="text-sm text-gray-600">Glucose and triglycerides are only given a status when the answer is yes.</p>
        <div className="mt-2 flex gap-4">
          <label className="inline-flex items-center gap-2">
            <input type="radio" name="fasting" checked={form.fasting === "yes"} onChange={() => patch({ fasting: "yes" })} />
            Yes
          </label>
          <label className="inline-flex items-center gap-2">
            <input type="radio" name="fasting" checked={form.fasting === "no"} onChange={() => patch({ fasting: "no" })} />
            No
          </label>
        </div>
      </fieldset>

      <div className="grid gap-4">
        {MARKERS.map((marker) => {
          const draft = form.markers[marker.id];
          return (
            <fieldset key={marker.id} className="border border-[var(--mint-light)] rounded-lg p-3">
              <legend className="px-1 font-medium">{marker.name}</legend>
              <p className="text-sm text-gray-600 mb-2">{marker.hint}</p>
              <div className="grid gap-2 sm:grid-cols-[1fr_140px_1fr_1fr]">
                <label className="text-sm">
                  Value
                  <input
                    className="field mt-1"
                    inputMode="decimal"
                    value={draft.value}
                    onChange={(event) => patchMarker(marker.id, { value: event.target.value })}
                  />
                </label>
                <label className="text-sm">
                  Unit
                  <select className="field mt-1" value={draft.unit} onChange={(event) => patchMarker(marker.id, { unit: event.target.value })}>
                    {marker.units.map((unit) => (
                      <option key={unit} value={unit}>{unit}</option>
                    ))}
                  </select>
                </label>
                <label className="text-sm">
                  Lab low <span className="font-normal text-gray-500">(optional)</span>
                  <input
                    className="field mt-1"
                    inputMode="decimal"
                    value={draft.labLow}
                    onChange={(event) => patchMarker(marker.id, { labLow: event.target.value })}
                  />
                </label>
                <label className="text-sm">
                  Lab high <span className="font-normal text-gray-500">(optional)</span>
                  <input
                    className="field mt-1"
                    inputMode="decimal"
                    value={draft.labHigh}
                    onChange={(event) => patchMarker(marker.id, { labHigh: event.target.value })}
                  />
                </label>
              </div>
            </fieldset>
          );
        })}
      </div>

      <div className="flex flex-wrap gap-3">
        <button className="btn" type="submit" disabled={busy}>{busy ? "Working…" : "Analyze"}</button>
      </div>

      <div>
        <h3 className="text-lg font-semibold">Try sample results</h3>
        <p className="text-sm text-gray-600 mb-2">Made-up numbers, not a real person. Try two dates if you want a trend line.</p>
        <div className="flex flex-wrap gap-2">
          {SAMPLES.map((sample) => (
            <button key={sample.id} className="btn btn-secondary" type="button" disabled={busy} onClick={() => onSample(sample.id)}>
              {sample.label}
            </button>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold">Or upload a lab PDF</h3>
        <p className="text-sm text-gray-600 mb-2">We read it in memory, show the numbers for you to edit, and then discard the file. A scanned page usually will not work.</p>
        <label className="btn inline-block cursor-pointer">
          Upload PDF
          <input
            className="hidden"
            type="file"
            accept="application/pdf,.pdf"
            onChange={(event) => {
              const file = event.target.files?.[0];
              event.target.value = "";
              if (file) onPdf(file);
            }}
          />
        </label>
      </div>
    </form>
  );
}
