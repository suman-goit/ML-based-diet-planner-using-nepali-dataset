# 🍛 Nepali Meal Planner (Prototype)

A working prototype: Django (REST API + ORM + Constraint Engine + ILP Engine)
backend, React frontend. Generates a personalized 3-day Nepali meal plan
based on a user's health assessment.

## Architecture

```
User Input (React form)
   → Frontend quick calc (BMI/BMR/TDEE, instant feedback)
   → Backend Django REST API
        → Django Form validation (planner/forms.py)
        → Constraint Engine (planner/constraint_engine.py)
              - BMI / BMR / TDEE
              - Calorie adjustment by goal
              - Macro targets
              - Filters Nepali food DB by food preference + medical conditions
        → ILP Engine (planner/ilp_engine.py, using PuLP)
              - Picks optimal integer servings of allowed foods per meal
              - Minimizes deviation from calorie target
              - Respects macro bounds + max/min items per meal
        → Meal Planner Generator (planner/meal_generator.py)
              - Builds Breakfast/Lunch/Dinner x 3 days
              - Persists MealPlan → DayPlan → Meal → MealItem (ORM)
   → React displays plan as Day 1–3 cards
```

## Project layout

```
backend/
  backend/            Django project settings/urls
  planner/
    models.py         ORM models (UserProfile, Food, MealPlan, DayPlan, Meal, MealItem)
    forms.py           Django Form used to validate the health assessment
    constraint_engine.py  BMI/BMR/TDEE + rule-based food filtering
    ilp_engine.py       PuLP-based integer optimizer for meal selection
    meal_generator.py   Orchestrates constraint + ILP engines, saves plan
    serializers.py       DRF serializers for API responses
    views.py             API endpoints (signup/login/assessment/plan)
    urls.py
    admin.py
    fixtures/nepali_foods.json   30-item Nepali food database seed
  requirements.txt
  manage.py

frontend/
  src/
    api.js            fetch helper; stores auth token in localStorage
                       so the browser "remembers" the logged-in user
    App.js             Routes: /login /signup / /assessment
    pages/Login.js
    pages/Signup.js
    pages/Home.js       Header + Start Assessment / Generate Plan + plan cards
    pages/Assessment.js Health assessment form (with instant client-side BMI/BMR/TDEE)
    styles.css
```

## Setup

### 1. Backend (Django)

```bash
cd nepali-meal-planner/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations planner
python manage.py migrate
python manage.py loaddata planner/fixtures/nepali_foods.json
python manage.py createsuperuser   # optional

python manage.py runserver
```

Backend runs at **http://localhost:8000**. API root: `http://localhost:8000/api/`.

### 2. Frontend (React)

```bash
cd frontend
npm install
npm start
```

Frontend runs at **http://localhost:3000** and proxies `/api` calls to
`http://localhost:8000` (see `"proxy"` in `package.json`).

## API endpoints

| Method | Endpoint                   | Purpose                                  |
|--------|-----------------------------|-------------------------------------------|
| POST   | /api/auth/signup/           | Create account, returns auth token        |
| POST   | /api/auth/login/            | Login, returns auth token                 |
| POST   | /api/auth/logout/           | Invalidate token                          |
| GET    | /api/auth/me/               | Current user + profile (used to "remember" login) |
| POST   | /api/assessment/            | Submit health assessment, computes BMI/BMR/TDEE/macros |
| POST   | /api/meal-plan/generate/    | Runs Constraint + ILP engines, builds 3-day plan |
| GET    | /api/meal-plan/latest/      | Fetch the active meal plan                |

Auth uses DRF Token Authentication. The React app stores the token in
`localStorage` and sends it as `Authorization: Token <token>` on every
request — this is what "remembers" a logged-in user across page reloads.

## Notes on this prototype

- SQLite database, `DEBUG=True`, permissive CORS — fine for local prototyping,
  **not** production-ready as-is.
- Macro split (25% protein / 50% carbs / 25% fat) and meal calorie split
  (30% breakfast / 40% lunch / 30% dinner) are simple fixed prototype rules —
  easy to tune in `constraint_engine.py`.
- The ILP engine uses the free CBC solver bundled with PuLP, so no external
  solver installation is required.
- Medical condition handling is intentionally simple: foods are tagged with
  `exclude_for_conditions` (comma-separated) and hard-excluded if they match
  the user's selected conditions (currently: diabetes, hypertension). Extend
  `MEDICAL_RULES` in `constraint_engine.py` for more conditions.
