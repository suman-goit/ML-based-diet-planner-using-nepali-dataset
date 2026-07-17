import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { api } from "../api";
import DeltaFeed from "../components/DeltaFeed";

export default function Home() {
  const { username, profile, ready } = useAuth();
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!profile) {
      setLoading(false);
      return;
    }
    api
      .assessmentHistory()
      .then(setHistory)
      .catch(() => setHistory(null))
      .finally(() => setLoading(false));
  }, [profile]);

  if (!ready || loading) {
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
          <h3>Welcome, {username}</h3>
          <p>You haven't completed a health assessment yet.</p>
          <Link to="/assessment" className="btn btn-primary" style={{ marginTop: 12 }}>
            Start Your Health Assessment
          </Link>
        </div>
      </div>
    );
  }

  const caloriePct = profile.target_calories
    ? Math.min(100, Math.round((profile.target_calories / 3000) * 100))
    : 0;
  const proteinPct = profile.target_protein_g
    ? Math.min(100, Math.round((profile.target_protein_g / 150) * 100))
    : 0;

  const previous = history && history.length > 1 ? history[1] : null;

  return (
    <div className="page">
      <div className="page-header">
        <span className="eyebrow">Home</span>
        <h1>Namaste, {username}</h1>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h3>Today's snapshot</h3>
        <div className="thali">
          <div className="thali-plate" style={{ "--pct": caloriePct }}>
            <div className="thali-reading">
              <span className="num">{Math.round(profile.target_calories)}</span>
              <span className="label">kcal target</span>
            </div>
          </div>
          <div className="thali-plate" style={{ "--pct": proteinPct }}>
            <div className="thali-reading">
              <span className="num">{Math.round(profile.target_protein_g)}g</span>
              <span className="label">protein target</span>
            </div>
          </div>
          <div className="thali-legend">
            <div className="row">
              <span className="swatch" style={{ background: "var(--terrace)" }} />
              BMI {profile.bmi} · BMR {Math.round(profile.bmr)} kcal
            </div>
            <div className="row">
              <span className="swatch" style={{ background: "var(--turmeric)" }} />
              TDEE {Math.round(profile.tdee)} kcal/day
            </div>
            <div className="row">
              <span className="swatch" style={{ background: "var(--indigo)" }} />
              Carbs {Math.round(profile.target_carbs_g)}g · Fat{" "}
              {Math.round(profile.target_fat_g)}g · Fiber {Math.round(profile.target_fiber_g)}g
            </div>
          </div>
        </div>
        <Link to="/assessment" className="btn btn-ghost btn-sm" style={{ marginTop: 16 }}>
          Retake assessment
        </Link>
      </div>

      <div className="card" style={{ marginBottom: 16 }}>
        <h3>Since your last assessment</h3>
        <DeltaFeed current={profile} previous={previous} />
      </div>

      <div className="card">
        <h3>Ready to eat?</h3>
        <p style={{ color: "var(--ink-soft)", marginBottom: 12 }}>
          Generate a 3-day meal plan built from your targets, medical conditions, and region.
        </p>
        <Link to="/meal-plan" className="btn btn-primary">
          Go to Meal Plan
        </Link>
      </div>
    </div>
  );
}
