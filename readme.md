# Panel to Table

Panel to Table turns eight common blood test numbers into food, activity, and recipe ideas. It does not diagnose a condition or replace a clinician. A result far from the usual range is flagged for a doctor, and food ideas are turned off for that marker.

The previous version read a genome file. That parser, the risk scores, and the chat box are gone. Saved tests stay in the browser.

## Run it locally

Frontend, from `frontend`:

```bash
npm install
npm run dev
```

Open http://localhost:3000.

Backend, from `backend`:

```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

Tests:

```bash
cd backend
source .venv/bin/activate
pytest
```

The API reads `CORS_ORIGINS` (default `http://localhost:3000,http://localhost:3001`). The site reads `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).

## What you can do

- Enter age, sex, test date, fasting yes or no, and any of the eight markers, with a unit and an optional lab range.
- Load one of three made-up sample profiles.
- Upload a text-based lab PDF. The numbers are shown for editing before anything is analyzed. A scanned PDF falls back to typing. Sample files live in `backend/sample_reports`.
- See a range bar, a see-a-doctor callout, food focus, and activity.
- Generate a new day of meals from Spoonacular. Pick one diet and any allergies, then generate again for a different day. Set `SPOONACULAR_API_KEY` on the API, or put it in gitignored `backend/.env`. The key stays on the server.
- Keep past tests in this browser, open the Results tab for a graph of each marker over time, and export JSON or CSV. JSON import restores that history on another device.
- Scan a package barcode, or search a food name. Nutrition numbers come from Open Food Facts and are not stored.

## Hosting

The frontend is a Next.js app and can go on Vercel. The API is FastAPI. `render.yaml` is a starting point for Render: set `CORS_ORIGINS` to the live site origin, and set `NEXT_PUBLIC_API_URL` on Vercel to the API origin. Free hosts often sleep; the loading screen says the server may be waking up.

Request bodies are not logged. PDFs are read in memory and discarded. History is not stored on the server.

## Sources

Ranges follow the notes on the home page: NIH Office of Dietary Supplements (vitamin D, vitamin B12, iron), ADA criteria for A1c and fasting glucose, NCEP ATP III adult lipids, and NHLBI pediatric lipid cut points. Recipes are from the American Heart Association and Cleveland Clinic.

Adult LDL under 130 mg/dL is treated as in range here, with under 100 called optimal and 100–129 called near optimal. Borderline starts at 130. The under-20 lipid column uses the NHLBI ages 10–19 cut points for anyone under 20.

## Not medical advice

Nothing in this project is a diagnosis, a treatment, or a reason to start a supplement. Very abnormal values tell the person to see a doctor and hide food tips for that marker.
