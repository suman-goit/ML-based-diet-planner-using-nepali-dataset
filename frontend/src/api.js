const API_BASE = "/api";

function getToken() {
  return localStorage.getItem("nmp_token");
}

export function saveSession(token, username) {
  localStorage.setItem("nmp_token", token);
  localStorage.setItem("nmp_username", username);
}

export function clearSession() {
  localStorage.removeItem("nmp_token");
  localStorage.removeItem("nmp_username");
}

export function getSavedUsername() {
  return localStorage.getItem("nmp_username");
}

async function request(path, { method = "GET", body } = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Token ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const message =
      typeof data === "object" ? Object.values(data).flat().join(" ") : "Request failed";
    throw new Error(message || `Request failed (${res.status})`);
  }
  return data;
}

export const api = {
  signup: (username, password) => request("/auth/signup/", { method: "POST", body: { username, password } }),
  login: (username, password) => request("/auth/login/", { method: "POST", body: { username, password } }),
  logout: () => request("/auth/logout/", { method: "POST" }),
  me: () => request("/auth/me/"),
  submitAssessment: (payload) => request("/assessment/", { method: "POST", body: payload }),
  generatePlan: () => request("/meal-plan/generate/", { method: "POST" }),
  latestPlan: () => request("/meal-plan/latest/"),
};

export { getToken };
