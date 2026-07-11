import React, { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";

const initialForm = {
  gender: "M",
  age: "",
  height_cm: "",
  weight_kg: "",
  activity_level: "sedentary",
  goal: "maintain",
  food_preference: "veg",
  medical_conditions: [],
};

const MEDICAL_OPTIONS = [
  { value: "diabetes", label: "Diabetes" },
  { value: "hypertension", label: "Hypertension" },
];

export default function Assessment({ onSaved }) {
  const [form, setForm] = useState(initialForm);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  // Quick instant feedback (frontend calculation), mirrors the backend
  // Constraint Engine formulas so the user sees numbers before submitting.
  const quickStats = useMemo(() => {
    const h = parseFloat(form.height_cm);
    const w = parseFloat(form.weight_kg);
    const age = parseInt(form.age, 10);
    if (!h || !w || !age) return null;

    const heightM = h / 100;
    const bmi = w / (heightM * heightM);

    let bmr = 10 * w + 6.25 * h - 5 * age;
    bmr += form.gender === "M" ? 5 : -161;

    const activityMultipliers = {
      sedentary: 1.2,
      light: 1.375,
      moderate: 1.55,
      active: 1.725,
      very_active: 1.9,
    };
    const tdee = bmr * activityMultipliers[form.activity_level];

    return { bmi: bmi.toFixed(1), bmr: bmr.toFixed(0), tdee: tdee.toFixed(0) };
  }, [form]);

  function update(field, value) {
    setForm((f) => ({ ...f, [field]: value }));
  }

  function toggleMedical(value) {
    setForm((f) => {
      const has = f.medical_conditions.includes(value);
      return {
        ...f,
        medical_conditions: has
          ? f.medical_conditions.filter((c) => c !== value)
          : [...f.medical_conditions, value],
      };
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const payload = {
        ...form,
        age: parseInt(form.age, 10),
        height_cm: parseFloat(form.height_cm),
        weight_kg: parseFloat(form.weight_kg),
        medical_conditions: form.medical_conditions.join(","),
      };
      const data = await api.submitAssessment(payload);
      onSaved(data);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <header className="app-header">
        <h2>Health Assessment</h2>
      </header>

      <main className="main">
        <form className="assessment-form" onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-field">
              <label>Gender</label>
              <select value={form.gender} onChange={(e) => update("gender", e.target.value)}>
                <option value="M">Male</option>
                <option value="F">Female</option>
              </select>
            </div>

            <div className="form-field">
              <label>Age</label>
              <input type="number" min="1" max="120" value={form.age}
                     onChange={(e) => update("age", e.target.value)} required />
            </div>

            <div className="form-field">
              <label>Height (cm)</label>
              <input type="number" step="0.1" value={form.height_cm}
                     onChange={(e) => update("height_cm", e.target.value)} required />
            </div>

            <div className="form-field">
              <label>Weight (kg)</label>
              <input type="number" step="0.1" value={form.weight_kg}
                     onChange={(e) => update("weight_kg", e.target.value)} required />
            </div>

            <div className="form-field">
              <label>Activity Level</label>
              <select value={form.activity_level} onChange={(e) => update("activity_level", e.target.value)}>
                <option value="sedentary">Sedentary</option>
                <option value="light">Light (1-3 days/week)</option>
                <option value="moderate">Moderate (3-5 days/week)</option>
                <option value="active">Active (6-7 days/week)</option>
                <option value="very_active">Very Active</option>
              </select>
            </div>

            <div className="form-field">
              <label>Goal</label>
              <select value={form.goal} onChange={(e) => update("goal", e.target.value)}>
                <option value="lose">Lose Weight</option>
                <option value="maintain">Maintain Weight</option>
                <option value="gain">Gain Weight</option>
              </select>
            </div>

            <div className="form-field">
              <label>Food Preference</label>
              <select value={form.food_preference} onChange={(e) => update("food_preference", e.target.value)}>
                <option value="veg">Vegetarian</option>
                <option value="nonveg">Non-Vegetarian</option>
                <option value="vegan">Vegan</option>
              </select>
            </div>

            <div className="form-field">
              <label>Medical Conditions</label>
              <div className="checkbox-row">
                {MEDICAL_OPTIONS.map((opt) => (
                  <label key={opt.value} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={form.medical_conditions.includes(opt.value)}
                      onChange={() => toggleMedical(opt.value)}
                    />
                    {opt.label}
                  </label>
                ))}
              </div>
            </div>
          </div>

          {quickStats && (
            <div className="quick-stats">
              <p>Instant estimate — BMI: <strong>{quickStats.bmi}</strong> | BMR: <strong>{quickStats.bmr} kcal</strong> | TDEE: <strong>{quickStats.tdee} kcal</strong></p>
            </div>
          )}

          {error && <p className="error">{error}</p>}

          <button type="submit" className="cta-btn" disabled={busy}>
            {busy ? "Saving..." : "Save Assessment"}
          </button>
        </form>
      </main>
    </div>
  );
}
