import React, { useEffect, useState } from "react";
import { Navigate, Route, Routes } from "react-router-dom";
import { api, getToken, clearSession } from "./api";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Home from "./pages/Home";
import Assessment from "./pages/Assessment";

export default function App() {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // On app load, if a token was saved in localStorage, fetch /auth/me/
  // so the user is automatically remembered/logged back in.
  useEffect(() => {
    async function bootstrap() {
      const token = getToken();
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const data = await api.me();
        setUser(data.username);
        setProfile(data.profile);
      } catch (err) {
        clearSession();
      } finally {
        setLoading(false);
      }
    }
    bootstrap();
  }, []);

  function handleAuthSuccess(username) {
    setUser(username);
    setProfile(null);
  }

  function handleLogout() {
    clearSession();
    setUser(null);
    setProfile(null);
  }

  if (loading) {
    return <div className="center-screen">Loading...</div>;
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={user ? <Navigate to="/" /> : <Login onSuccess={handleAuthSuccess} />}
      />
      <Route
        path="/signup"
        element={user ? <Navigate to="/" /> : <Signup onSuccess={handleAuthSuccess} />}
      />
      <Route
        path="/"
        element={
          user ? (
            <Home username={user} profile={profile} setProfile={setProfile} onLogout={handleLogout} />
          ) : (
            <Navigate to="/login" />
          )
        }
      />
      <Route
        path="/assessment"
        element={
          user ? (
            <Assessment onSaved={(p) => setProfile(p)} />
          ) : (
            <Navigate to="/login" />
          )
        }
      />
    </Routes>
  );
}
