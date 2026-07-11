import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const MEAL_ORDER = ["breakfast", "lunch", "dinner"];
const MEAL_LABEL = { breakfast: "Breakfast", lunch: "Lunch", dinner: "Dinner" };

export default function Home({ username, profile, setProfile, onLogout }) {
  const [plan, setPlan] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    async function loadPlan() {
      try {
        const data = await api.latestPlan();
        setPlan(data);
      } catch (err) {
        setPlan(null); // no plan yet - fine
      }
    }
    if (profile) loadPlan();
  }, [profile]);

  async function handleGeneratePlan() {
    setGenerating(true);
    setError("");
    try {
      const data = await api.generatePlan();
      setPlan(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  }

  return (
    <div className="page">
      <header className="app-header">
        <div>
          <h2>Nepali Meal Planner</h2>
          <p>Welcome, {username}</p>
        </div>
        <button className="link-btn" onClick={onLogout}>Logout</button>
      </header>

      <main className="main">
        <button className="cta-btn" onClick={() => navigate("/assessment")}>
          {profile ? "Update Your Health Assessment" : "Start Your Health Assessment"}
        </button>

        {profile && (
          <>
            <div className="summary-cards">
              <SummaryCard label="BMI" value={profile.bmi} />
              <SummaryCard label="BMR" value={`${profile.bmr} kcal`} />
              <SummaryCard label="TDEE" value={`${profile.tdee} kcal`} />
              <SummaryCard label="Daily Target" value={`${profile.target_calories} kcal`} />
            </div>

            <button className="cta-btn secondary" onClick={handleGeneratePlan} disabled={generating}>
              {generating ? "Generating..." : "Generate Meal Plan"}
            </button>
            {error && <p className="error">{error}</p>}
          </>
        )}

        {plan && (
          <section className="plan-preview">
            <h3>Your 3-Day Meal Plan</h3>
            <div className="day-grid">
              {plan.days.map((day) => (
                <div className="day-card" key={day.id}>
                  <h4>Day {day.day_number}</h4>
                  {MEAL_ORDER.map((mealType) => {
                    const meal = day.meals.find((m) => m.meal_type === mealType);
                    if (!meal) return null;
                    return (
                      <div className="meal-block" key={meal.id}>
                        <p className="meal-title">
                          {MEAL_LABEL[mealType]}{" "}
                          <span className="meal-cals">({meal.total_calories} kcal)</span>
                        </p>
                        <ul>
                          {meal.items.map((item) => (
                            <li key={item.id}>
                              {item.servings} × {item.food.name}
                            </li>
                          ))}
                        </ul>
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </section>
        )}
      </main>

      <footer className="app-footer">Powered by Django + React</footer>
    </div>
  );
}

function SummaryCard({ label, value }) {
  return (
    <div className="summary-card">
      <p className="summary-label">{label}</p>
      <p className="summary-value">{value}</p>
    </div>
  );
}
