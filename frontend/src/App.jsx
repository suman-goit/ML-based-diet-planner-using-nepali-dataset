import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import Navbar from "./components/Navbar";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Home from "./pages/Home";
import Assessment from "./pages/Assessment";
import MealPlan from "./pages/MealPlan";
import History from "./pages/History";
import Profile from "./pages/Profile";

function ProtectedShell({ children }) {
  const { token, ready } = useAuth();
  if (!ready) {
    return (
      <div className="center-loading" style={{ minHeight: "100vh" }}>
        <div className="spinner" />
      </div>
    );
  }
  if (!token) return <Navigate to="/login" replace />;
  return (
    <div className="app-shell">
      <Navbar />
      {children}
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route
        path="/"
        element={
          <ProtectedShell>
            <Home />
          </ProtectedShell>
        }
      />
      <Route
        path="/assessment"
        element={
          <ProtectedShell>
            <Assessment />
          </ProtectedShell>
        }
      />
      <Route
        path="/meal-plan"
        element={
          <ProtectedShell>
            <MealPlan />
          </ProtectedShell>
        }
      />
      <Route
        path="/history"
        element={
          <ProtectedShell>
            <History />
          </ProtectedShell>
        }
      />
      <Route
        path="/profile"
        element={
          <ProtectedShell>
            <Profile />
          </ProtectedShell>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
