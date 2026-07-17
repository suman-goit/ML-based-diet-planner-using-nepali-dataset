# Nepali Diet Planner — Full Stack

```
nepali-diet-planner/
├── backend/    Django + DRF API (see backend/README.md)
└── frontend/   React + Vite client (see frontend/README.md)
```

## Run both together

**Terminal 1 — backend:**
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py train_decision_tree
python manage.py runserver
```
Runs at http://localhost:8000, API under `/api/`.

**Terminal 2 — frontend:**
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Runs at http://localhost:5173 and talks to the backend via `VITE_API_URL`.

Open http://localhost:5173, sign up, complete the health assessment, then
generate a meal plan.

## Testing status

I don't have outbound network access in my sandbox, so I could not
`pip install`/`npm install` and actually execute either server end-to-end
here. What I did do:
- Wrote `backend/core/models.py` to match the migration field-for-field, and
  `ilp_engine.py` + the two management commands to match the exact function
  signatures your existing `views.py`/`serializers.py`/`decision_tree.py`
  already call.
- Syntax-checked every backend `.py` file with `python -m py_compile` (all pass).
- Manually re-derived the BMR/TDEE/macro math and the ILP nutrient-scaling
  math in standalone scripts to confirm the formulas are dimensionally
  correct and produce sane numbers (see backend/README.md for the specific
  checks).
- Cross-checked every frontend API call against the exact serializer field
  names (`MealPlanSerializer` → `days` → `meals` → `items` → `food`, etc.)
  so the two sides should line up without translation.

Please run the smoke test in `backend/README.md` on your machine first —
that's the first real end-to-end execution of this combination. If
`generate_meal_plan` comes back empty for a given profile, it's almost
always because the region/diet/allergy filters left too few candidate foods
— check `Food.objects.count()` after `seed_data` and loosen a filter to
confirm the pipeline itself works before debugging further.

## What's new since the frontend-only pass

- Filled in the backend's three missing pieces: `models.py`, `ilp_engine.py`,
  `seed_data.py`, `train_decision_tree.py`.
- Fixed a real bug in `constraint_engine.DIET_ALLOWED`: Vegan was previously
  disjoint from Vegetarian, which meant Vegan users would never match any
  food. Now Vegan is a proper subset (see backend/README.md for detail).
