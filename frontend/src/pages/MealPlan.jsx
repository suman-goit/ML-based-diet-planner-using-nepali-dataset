import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../api";
import { useAuth } from "../context/AuthContext";
import MealCard from "../components/MealCard";

export default function MealPlan() {
  const { profile } = useAuth();
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [activeDay, setActiveDay] = useState(1);
  const [regeneratingKey, setRegeneratingKey] = useState(null);

  useEffect(() => {
    loadLatest();
  }, []);

  async function loadLatest() {
    setLoading(true);
    try {
      const data = await api.mealPlanLatest();
      setPlan(data);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setPlan(null);
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleGenerate() {
    setGenerating(true);
    setError("");
    try {
      const data = await api.generateMealPlan();
      setPlan(data);
      setActiveDay(1);
    } catch (err) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  }

  async function handleRegenerate(dayNumber, mealType) {
    const key = `${dayNumber}-${mealType}`;
    setRegeneratingKey(key);
    setError("");
    try {
      const updatedDay = await api.regenerateMeal(dayNumber, mealType);
      setPlan((prev) => ({
        ...prev,
        days: prev.days.map((d) => (d.day_number === dayNumber ? updatedDay : d)),
      }));
    } catch (err) {
      setError(err.message);
    } finally {
      setRegeneratingKey(null);
    }
  }

  if (loading) {
    return (
      <div className="center-loading">
        <div className="spinner" />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="page">
        <div className="empty-state card">
          <h3>Complete a health assessment first</h3>
          <p>We need your targets before we can build a meal plan.</p>
          <Link to="/assessment" className="btn btn-primary" style={{ marginTop: 12 }}>
            Start Your Health Assessment
          </Link>
        </div>
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="page">
        <div className="empty-state card">
          <h3>No meal plan yet</h3>
          <p>Generate a 3-day plan built from your targets and constraints.</p>
          {error && <div className="error-banner" style={{ marginTop: 12 }}>{error}</div>}
          <button
            className="btn btn-primary"
            onClick={handleGenerate}
            disabled={generating}
            style={{ marginTop: 12 }}
          >
            {generating ? "Generating…" : "Generate Meal Plan"}
          </button>
        </div>
      </div>
    );
  }

  const day = plan.days.find((d) => d.day_number === activeDay) || plan.days[0];
  const dayTotals = day.meals.reduce(
    (acc, m) => {
      const t = m.totals || {};
      acc.calories += t.calories || 0;
      acc.protein_g += t.protein_g || 0;
      acc.carbs_g += t.carbs_g || 0;
      acc.fat_g += t.fat_g || 0;
      return acc;
    },
    { calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0 }
  );

  const mealOrder = ["Breakfast", "Lunch", "Dinner"];
  const sortedMeals = [...day.meals].sort(
    (a, b) => mealOrder.indexOf(a.meal_type) - mealOrder.indexOf(b.meal_type)
  );

  return (
    <div className="page">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        <div>
          <span className="eyebrow">Meal Plan</span>
          <h1>Your 3-day plan</h1>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={handleGenerate} disabled={generating}>
          {generating ? "Regenerating…" : "↻ Generate new plan"}
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="plan-summary">
        <div className="stat-block">
          <div className="val">{Math.round(dayTotals.calories)}</div>
          <div className="lbl">Calories · target {Math.round(profile.target_calories)}</div>
        </div>
        <div className="stat-block">
          <div className="val">{Math.round(dayTotals.protein_g)}g</div>
          <div className="lbl">Protein · target {Math.round(profile.target_protein_g)}g</div>
        </div>
        <div className="stat-block">
          <div className="val">{Math.round(dayTotals.carbs_g)}g</div>
          <div className="lbl">Carbs · target {Math.round(profile.target_carbs_g)}g</div>
        </div>
        <div className="stat-block">
          <div className="val">{Math.round(dayTotals.fat_g)}g</div>
          <div className="lbl">Fat · target {Math.round(profile.target_fat_g)}g</div>
        </div>
      </div>

      <div className="day-tabs">
        {plan.days.map((d) => (
          <button
            key={d.id}
            className={d.day_number === activeDay ? "active" : ""}
            onClick={() => setActiveDay(d.day_number)}
          >
            Day {d.day_number}
          </button>
        ))}
      </div>

      {sortedMeals.map((meal) => (
        <MealCard
          key={meal.id}
          meal={meal}
          onRegenerate={() => handleRegenerate(day.day_number, meal.meal_type)}
          regenerating={regeneratingKey === `${day.day_number}-${meal.meal_type}`}
        />
      ))}
    </div>
  );
}
