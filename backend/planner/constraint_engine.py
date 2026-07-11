"""
Constraint Engine
=================
Pure business-rule layer, deliberately separated from the ILP engine.

Responsibilities:
1. Calculate BMI, BMR (Mifflin-St Jeor), TDEE.
2. Apply goal-based calorie adjustment (lose / maintain / gain).
3. Derive macro targets (protein/carbs/fat in grams).
4. Filter the Food queryset down to what is ALLOWED for this user, based on
   food preference (veg/nonveg/vegan) and medical conditions
   (diabetes -> low sugar, hypertension -> low sodium, etc).

The ILP engine then only ever sees an already-legal set of foods and just
has to optimise quantities against the numeric targets.
"""

from .models import Food

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

GOAL_CALORIE_ADJUSTMENT = {
    "lose": -500,
    "maintain": 0,
    "gain": 400,
}

# Macro split (percent of total calories) - simple fixed prototype split.
MACRO_SPLIT = {"protein": 0.25, "carbs": 0.5, "fat": 0.25}

CALORIES_PER_G = {"protein": 4, "carbs": 4, "fat": 9}

# Medical-condition -> nutrient rule (used both to filter foods and to
# tighten ILP bounds later if desired).
MEDICAL_RULES = {
    "diabetes": {"max_sugar_g_per_meal": 10},
    "hypertension": {"max_sodium_mg_per_meal": 500},
}


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)


def calculate_bmr(gender: str, weight_kg: float, height_cm: float, age: int) -> float:
    # Mifflin-St Jeor Equation
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if gender == "M":
        return round(base + 5, 2)
    return round(base - 161, 2)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)
    return round(bmr * multiplier, 2)


def calculate_targets(profile) -> dict:
    """Given a UserProfile instance (unsaved values are fine too),
    return a dict with bmi/bmr/tdee/target_calories/macros."""
    bmi = calculate_bmi(profile.weight_kg, profile.height_cm)
    bmr = calculate_bmr(profile.gender, profile.weight_kg, profile.height_cm, profile.age)
    tdee = calculate_tdee(bmr, profile.activity_level)

    adjustment = GOAL_CALORIE_ADJUSTMENT.get(profile.goal, 0)
    target_calories = max(1200, tdee + adjustment)  # never go below a safe floor

    target_protein_g = round((target_calories * MACRO_SPLIT["protein"]) / CALORIES_PER_G["protein"], 1)
    target_carbs_g = round((target_calories * MACRO_SPLIT["carbs"]) / CALORIES_PER_G["carbs"], 1)
    target_fat_g = round((target_calories * MACRO_SPLIT["fat"]) / CALORIES_PER_G["fat"], 1)

    return {
        "bmi": bmi,
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": round(target_calories, 1),
        "target_protein_g": target_protein_g,
        "target_carbs_g": target_carbs_g,
        "target_fat_g": target_fat_g,
    }


def allowed_foods_for(profile, meal_type: str):
    """Return a queryset of Food objects legal for this user & meal slot,
    applying food-preference and medical-condition constraints."""
    qs = Food.objects.filter(suitable_meals__icontains=meal_type)

    # --- Food preference constraint ---
    if profile.food_preference == "vegan":
        qs = qs.filter(diet_tag="vegan")
    elif profile.food_preference == "veg":
        qs = qs.filter(diet_tag__in=["veg", "vegan"])
    # nonveg users can eat anything (veg, vegan, nonveg)

    # --- Medical condition constraints (hard exclude) ---
    conditions = profile.medical_conditions_list()
    for food in list(qs):
        excluded_for = food.exclude_list()
        if any(c in excluded_for for c in conditions):
            qs = qs.exclude(pk=food.pk)

    return qs


def meal_calorie_targets(target_calories: float) -> dict:
    """Split the daily calorie target across breakfast/lunch/dinner."""
    return {
        "breakfast": round(target_calories * 0.30, 1),
        "lunch": round(target_calories * 0.40, 1),
        "dinner": round(target_calories * 0.30, 1),
    }
