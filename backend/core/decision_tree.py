"""
Decision Tree — medical suitability (Hypertension, Diabetes).

Trained on synthetic labels generated from documented thresholds
(WHO sodium guidance / ADA sugar guidance — see architecture doc Section 4),
not from user behavior data. Shallow (max_depth=4) for explainability.
"""
import os
import joblib
import pandas as pd
from django.conf import settings
from sklearn.tree import DecisionTreeClassifier

SODIUM_THRESHOLD = 400  # mg per 100g — WHO guidance proxy for Hypertension
SUGAR_THRESHOLD = 15    # g per 100g — ADA guidance proxy for Diabetes

MODEL_PATH = os.path.join(settings.BASE_DIR, "core", "ml_artifacts", "decision_tree.joblib")

FEATURE_COLS = ["sodium_mg", "sugar_g", "carbs_g", "fat_g", "calories",
                 "condition_Diabetes", "condition_Hypertension"]


def build_training_data(foods_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, food in foods_df.iterrows():
        for condition in ["Hypertension", "Diabetes"]:
            label = 1
            if condition == "Hypertension" and food["sodium_mg"] > SODIUM_THRESHOLD:
                label = 0
            if condition == "Diabetes" and food["sugar_g"] > SUGAR_THRESHOLD:
                label = 0
            rows.append({
                "sodium_mg": food["sodium_mg"], "sugar_g": food["sugar_g"],
                "carbs_g": food["carbs_g"], "fat_g": food["fat_g"],
                "calories": food["calories"], "condition": condition,
                "suitable": label,
            })
    df = pd.DataFrame(rows)
    ohe = pd.get_dummies(df["condition"], prefix="condition")
    for col in ["condition_Diabetes", "condition_Hypertension"]:
        if col not in ohe.columns:
            ohe[col] = False
    return pd.concat([df.drop(columns=["condition"]), ohe], axis=1)


def train_and_save(foods_df: pd.DataFrame) -> DecisionTreeClassifier:
    train_df = build_training_data(foods_df)
    X = train_df[FEATURE_COLS]
    y = train_df["suitable"]
    clf = DecisionTreeClassifier(max_depth=4, random_state=42)
    clf.fit(X, y)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(clf, MODEL_PATH)
    return clf


_model_cache = None


def get_model():
    global _model_cache
    if _model_cache is None:
        if os.path.exists(MODEL_PATH):
            _model_cache = joblib.load(MODEL_PATH)
        else:
            raise FileNotFoundError(
                "Decision tree not trained yet. Run: python manage.py train_decision_tree"
            )
    return _model_cache


def is_suitable(food, condition: str) -> bool:
    """food: Food model instance or dict-like with sodium_mg/sugar_g/carbs_g/fat_g/calories.
    condition: 'Hypertension' | 'Diabetes' | anything else -> always suitable (out of scope)."""
    if condition not in ("Hypertension", "Diabetes"):
        return True
    model = get_model()

    def _get(obj, key):
        if hasattr(obj, key):
            return getattr(obj, key)
        return obj[key]

    row = {
        "sodium_mg": _get(food, "sodium_mg"),
        "sugar_g": _get(food, "sugar_g"),
        "carbs_g": _get(food, "carbs_g"),
        "fat_g": _get(food, "fat_g"),
        "calories": _get(food, "calories"),
        "condition_Diabetes": condition == "Diabetes",
        "condition_Hypertension": condition == "Hypertension",
    }
    X = pd.DataFrame([row])[FEATURE_COLS]
    return bool(model.predict(X)[0])


def allowed_foods_for(foods_qs, medical_conditions: list[str]):
    """Filter a Food queryset/list down to items suitable for ALL of the
    person's tracked conditions (Hypertension, Diabetes). Untracked
    conditions (Anaemia, Celiac, etc.) are out of scope -> pass-through."""
    tracked = [c for c in medical_conditions if c in ("Hypertension", "Diabetes")]
    if not tracked:
        return list(foods_qs)
    return [f for f in foods_qs if all(is_suitable(f, c) for c in tracked)]
