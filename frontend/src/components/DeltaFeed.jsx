const TRACKED = [
  { key: "weight_kg", label: "Weight", unit: "kg" },
  { key: "bmi", label: "BMI", unit: "" },
  { key: "target_calories", label: "Target calories", unit: "kcal" },
  { key: "target_protein_g", label: "Target protein", unit: "g" },
];

export default function DeltaFeed({ current, previous }) {
  if (!previous) {
    return (
      <p style={{ color: "var(--ink-soft)", fontSize: "0.88rem" }}>
        This is your first assessment — future changes will show up here.
      </p>
    );
  }

  const rows = TRACKED.map(({ key, label, unit }) => {
    const currentVal = current[key];
    const prevVal = previous[key];
    if (currentVal == null || prevVal == null) return null;
    const diff = Math.round((currentVal - prevVal) * 10) / 10;
    return { key, label, unit, diff, currentVal };
  }).filter(Boolean);

  if (rows.length === 0) {
    return (
      <p style={{ color: "var(--ink-soft)", fontSize: "0.88rem" }}>
        No comparable changes since your last assessment.
      </p>
    );
  }

  return (
    <div className="delta-feed">
      {rows.map((row) => (
        <div className="delta-row" key={row.key}>
          <span>{row.label}</span>
          <span
            className={
              "delta-val " + (row.diff > 0 ? "delta-up" : row.diff < 0 ? "delta-down" : "")
            }
          >
            {row.diff === 0 ? "—" : row.diff > 0 ? `+${row.diff}` : row.diff} {row.unit}
          </span>
        </div>
      ))}
    </div>
  );
}
