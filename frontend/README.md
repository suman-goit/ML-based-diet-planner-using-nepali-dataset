# Nepali Diet Planner — Frontend (React + Vite)

Talks to the Django backend described in `nepali-diet-planner-architecture.md`.
No UI library — plain CSS with design tokens in `src/styles.css`.

## Setup

```bash
cd frontend
npm install
cp .env.example .env      # points at http://localhost:8000/api by default
npm run dev               # http://localhost:5173
```

Make sure the Django backend is running first (`python manage.py runserver`) with
CORS open (it already is — `CORS_ALLOW_ALL_ORIGINS = True` in `settings.py`).

## Pages (matches architecture doc §6)

| Route | Page |
|---|---|
| `/login`, `/signup` | Auth |
| `/` | Home — thali-style calorie/protein dial, delta feed vs previous assessment |
| `/assessment` | Health assessment form → `POST /api/assessment/` |
| `/meal-plan` | 3-day plan, day tabs, per-meal Regenerate button |
| `/history` | Assessment history table, delete row, "Download as PDF" (browser print) |
| `/profile` | Latest assessment summary + logout |

## How auth works

Token is stored in `localStorage` (`ndp_token`). `AuthContext` calls
`GET /api/auth/me/` on load to restore `username` + `latest_profile`, and
after every assessment submit/delete so Home/Meal Plan targets stay in sync.

## Known gaps (match backend's own "Known gaps" list)

- "Download as PDF" on History currently triggers the browser print dialog —
  there's no `/api/assessment/history/pdf/` endpoint yet, so this is a stand-in.
- No Groceries/favorites page (explicitly out of scope in the architecture doc).
- No Google OAuth (not yet scoped).
- Loading states are minimal spinners; no skeleton screens.

## Next 2–3 day feature ideas

- Wire a real PDF export endpoint on the backend and swap `window.print()` for
  a fetch-and-download of that file.
- Show the Decision Tree's rule path somewhere in the Meal Plan UI ("excluded
  for Hypertension: sodium above threshold") since explainability was a
  stated design goal.
- Add allergy/dislike fields to the assessment form once the backend model
  gains them (architecture doc §8 flags this as recommended-not-implemented).
- Age-bracket RDA/BDP override banner on Home once `constraint_engine` wires
  those tables in (README's "Known gaps" #1).
