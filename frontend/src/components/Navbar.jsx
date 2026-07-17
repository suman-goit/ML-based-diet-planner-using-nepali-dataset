import { useState, useRef, useEffect } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { username, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    function onClick(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  function handleLogout() {
    logout();
    navigate("/login");
  }

  const initial = (username || "?").charAt(0).toUpperCase();

  return (
    <div style={{ position: "relative" }}>
      <header className="navbar">
        <div className="brand">
          भोजन <small>Nepali Diet Planner</small>
        </div>
        <nav>
          <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
            Home
          </NavLink>
          <NavLink to="/meal-plan" className={({ isActive }) => (isActive ? "active" : "")}>
            Meal Plan
          </NavLink>
          <NavLink to="/history" className={({ isActive }) => (isActive ? "active" : "")}>
            Health Assessment History
          </NavLink>
          <button
            className="avatar-circle"
            onClick={() => setMenuOpen((v) => !v)}
            aria-label="Account menu"
          >
            {initial}
          </button>
        </nav>
      </header>
      {menuOpen && (
        <div className="avatar-menu" ref={menuRef}>
          <NavLink to="/profile" onClick={() => setMenuOpen(false)}>
            Profile
          </NavLink>
          <button onClick={handleLogout}>Logout</button>
        </div>
      )}
    </div>
  );
}
