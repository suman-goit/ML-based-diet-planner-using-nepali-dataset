const MEAL_ICON = { Breakfast: "☀", Lunch: "🍽", Dinner: "🌙" };

export default function MealCard({ meal, onRegenerate, regenerating }) {
  const totals = meal.totals || {};
  return (
    <div className="meal-card">
      <div className="meal-card-head">
        <h3>
          <span className="meal-type-tag">{meal.meal_type}</span>
          {meal.meal_type}
        </h3>
        <button
          className="btn btn-ghost btn-sm"
          onClick={onRegenerate}
          disabled={regenerating}
        >
          {regenerating ? "Regenerating…" : "↻ Regenerate"}
        </button>
      </div>

      {meal.items.length === 0 ? (
        <p style={{ color: "var(--ink-soft)", fontSize: "0.85rem" }}>
          No items could be found for this meal within the current constraints.
        </p>
      ) : (
        meal.items.map((item) => (
          <div className="food-item" key={item.id}>
            <div>
              <div className="fname">{item.food.name}</div>
              {item.food.nepali_name && (
                <div className="fnepali">{item.food.nepali_name}</div>
              )}
            </div>
            <div className="fgrams">
              {item.grams}g · {Math.round(item.food.calories * (item.grams / 100))} kcal
            </div>
          </div>
        ))
      )}

      <div className="meal-totals">
        <span>{Math.round(totals.calories || 0)} kcal</span>
        <span>P {Math.round(totals.protein_g || 0)}g</span>
        <span>C {Math.round(totals.carbs_g || 0)}g</span>
        <span>F {Math.round(totals.fat_g || 0)}g</span>
      </div>
    </div>
  );
}
