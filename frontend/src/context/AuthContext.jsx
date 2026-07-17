import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("ndp_token"));
  const [username, setUsername] = useState(() => localStorage.getItem("ndp_username"));
  const [profile, setProfile] = useState(null); // latest UserProfile assessment, or null
  const [ready, setReady] = useState(false);

  const refreshMe = useCallback(async () => {
    if (!localStorage.getItem("ndp_token")) {
      setProfile(null);
      setReady(true);
      return;
    }
    try {
      const data = await api.me();
      setUsername(data.username);
      setProfile(data.latest_profile || null);
    } catch (e) {
      // token invalid/expired
      logout();
    } finally {
      setReady(true);
    }
  }, []);

  useEffect(() => {
    refreshMe();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function login(tokenValue, usernameValue) {
    localStorage.setItem("ndp_token", tokenValue);
    localStorage.setItem("ndp_username", usernameValue);
    setToken(tokenValue);
    setUsername(usernameValue);
    refreshMe();
  }

  function logout() {
    localStorage.removeItem("ndp_token");
    localStorage.removeItem("ndp_username");
    setToken(null);
    setUsername(null);
    setProfile(null);
  }

  return (
    <AuthContext.Provider
      value={{ token, username, profile, setProfile, ready, login, logout, refreshMe }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
