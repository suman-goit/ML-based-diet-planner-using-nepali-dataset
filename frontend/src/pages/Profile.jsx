import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { username, profile, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="page">
      <div className="page-header">
        <span className="eyebrow">Profile</span>
        <h1>{username}</h1>
      </div>

      <div className="card" style={{ maxWidth: 480 }}>
        <h3>Latest assessment</h3>
        {profile ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 8, fontSize: "0.9rem" }}>
            <div>Gender: {profile.gender}</div>
            <div>Age: {profile.age}</div>
            <div>
              Height / Weight: {profile.height_cm} cm / {profile.weight_kg} kg
            </div>
            <div>Activity level: {profile.activity_level}</div>
            <div>Goal: {profile.goal}</div>
            <div>Food preference: {profile.food_preference}</div>
            <div>Region: {profile.region}</div>
            <div>Medical conditions: {profile.medical_conditions || "None"}</div>
            <div>Allergies: {profile.allergies || "None"}</div>
          </div>
        ) : (
          <p style={{ color: "var(--ink-soft)" }}>No assessment on record yet.</p>
        )}
      </div>

      <button className="btn btn-danger" onClick={handleLogout} style={{ marginTop: 20 }}>
        Logout
      </button>
    </div>
  );
}
