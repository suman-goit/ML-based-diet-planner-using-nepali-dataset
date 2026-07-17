const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = localStorage.getItem("ndp_token");
    if (token) headers["Authorization"] = `Token ${token}`;
  }

  let res;
  try {
    res = await fetch(`${API_BASE}/${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (e) {
    throw new ApiError(
      "Can't reach the server. Is the Django backend running on port 8000?",
      0
    );
  }

  if (res.status === 204) return null;

  let data = null;
  try {
    data = await res.json();
  } catch {
    // no body
  }

  if (!res.ok) {
    const message =
      (data && (data.detail || firstError(data))) || `Request failed (${res.status})`;
    throw new ApiError(message, res.status, data);
  }
  return data;
}

function firstError(data) {
  if (typeof data !== "object" || !data) return null;
  const key = Object.keys(data)[0];
  const val = data[key];
  return Array.isArray(val) ? `${key}: ${val[0]}` : `${key}: ${val}`;
}

export const api = {
  signup: (username, password) =>
    request("auth/signup/", { method: "POST", body: { username, password }, auth: false }),
  login: (username, password) =>
    request("auth/login/", { method: "POST", body: { username, password }, auth: false }),
  logout: () => request("auth/logout/", { method: "POST" }),
  me: () => request("auth/me/"),

  createAssessment: (payload) => request("assessment/", { method: "POST", body: payload }),
  assessmentLatest: () => request("assessment/latest/"),
  assessmentHistory: () => request("assessment/history/"),
  deleteAssessment: (id) => request(`assessment/${id}/`, { method: "DELETE" }),

  generateMealPlan: () => request("meal-plan/generate/", { method: "POST" }),
  mealPlanLatest: () => request("meal-plan/latest/"),
  regenerateMeal: (day_number, meal_type) =>
    request("meal-plan/regenerate-meal/", { method: "POST", body: { day_number, meal_type } }),
};

export { ApiError };
