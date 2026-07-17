import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

export default function History() {
  const { refreshMe } = useAuth();
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    load();
  }, []);

  async function load() {
    setLoading(true);
    try {
      const data = await api.assessmentHistory();
      setHistory(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id) {
    setDeletingId(id);
    try {
      await api.deleteAssessment(id);
      setHistory((h) => h.filter((row) => row.id !== id));
      await refreshMe();
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingId(null);
    }
  }

  function handleDownloadPdf() {
    window.print();
  }

  if (loading) {
    return (
      <div className="center-loading">
        <div className="spinner" />
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        <div>
          <span className="eyebrow">History</span>
          <h1>Health Assessment History</h1>
        </div>
        {history && history.length > 0 && (
          <button className="btn btn-ghost btn-sm" onClick={handleDownloadPdf}>
            Download as PDF
          </button>
        )}
      </div>

      {error && <div className="error-banner">{error}</div>}

      {!history || history.length === 0 ? (
        <div className="empty-state card">
          <h3>Your history is clear — start your first assessment.</h3>
          <Link to="/assessment" className="btn btn-primary" style={{ marginTop: 12 }}>
            Start Your Health Assessment
          </Link>
        </div>
      ) : (
        <div className="card" style={{ padding: 0, overflowX: "auto" }}>
          <table className="history-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Weight</th>
                <th>BMI</th>
                <th>Goal</th>
                <th>Target kcal</th>
                <th>Target protein</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {history.map((row) => (
                <tr key={row.id}>
                  <td>{new Date(row.created_at).toLocaleString()}</td>
                  <td className="mono">{row.weight_kg} kg</td>
                  <td className="mono">{row.bmi}</td>
                  <td>{row.goal}</td>
                  <td className="mono">{Math.round(row.target_calories)}</td>
                  <td className="mono">{Math.round(row.target_protein_g)}g</td>
                  <td>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDelete(row.id)}
                      disabled={deletingId === row.id}
                    >
                      {deletingId === row.id ? "…" : "Delete"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
