"""
Constraint Engine — "what should this person eat, how much, and what's allowed?"

Pipeline: BMI -> BMR (Mifflin-St Jeor) -> TDEE -> target calories (goal-adjusted)
-> target macros (ratio-based) -> filtered food list (diet/allergy/region/
availability + Decision Tree medical filter).
"""
from . import decision_tree
from .models import Food

ACTIVITY_MULTIPLIER = {
    "Sedentary": 1.2,
    "Lightly Active": 1.375,
    "Moderate": 1.55,
    "Very Active": 1.725,
    "Extra Active": 1.9,
}

GOAL_CALORIE_ADJUSTMENT = {
    "Weight Loss": -500,
    "Maintenance": 0,
    "Healthy Living": 0,
    "Muscle Gain": 300,
}

# macro ratio of target calories: (protein, carbs, fat) — fiber/omega3 via fixed g/1000kcal
MACRO_RATIO = {
    "Weight Loss": (0.30, 0.40, 0.30),
    "Maintenance": (0.20, 0.55, 0.25),
    "Healthy Living": (0.20, 0.55, 0.25),
    "Muscle Gain": (0.30, 0.45, 0.25),
}

FIBER_G_PER_1000KCAL = 14  # standard dietary guideline
OMEGA3_G_PER_DAY = 1.6     # RDA-ish daily target, flat


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    if gender.strip().lower() == "male":
        return round(base + 5, 1)
    return round(base - 161, 1)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    mult = ACTIVITY_MULTIPLIER.get(activity_level, 1.2)
    return round(bmr * mult, 1)


def calculate_targets(profile) -> dict:
    """profile: UserProfile instance (unsaved is fine, just needs the fields)."""
    bmi = calculate_bmi(profile.weight_kg, profile.height_cm)
    bmr = calculate_bmr(profile.weight_kg, profile.height_cm, profile.age, profile.gender)
    tdee = calculate_tdee(bmr, profile.activity_level)

    target_calories = tdee + GOAL_CALORIE_ADJUSTMENT.get(profile.goal, 0)
    target_calories = max(target_calories, 1200)  # safety floor

    p_ratio, c_ratio, f_ratio = MACRO_RATIO.get(profile.goal, MACRO_RATIO["Maintenance"])
    target_protein_g = round((target_calories * p_ratio) / 4, 1)
    target_carbs_g = round((target_calories * c_ratio) / 4, 1)
    target_fat_g = round((target_calories * f_ratio) / 9, 1)
    target_fiber_g = round((target_calories / 1000) * FIBER_G_PER_1000KCAL, 1)
    target_omega3_g = OMEGA3_G_PER_DAY

    return {
        "bmi": bmi, "bmr": bmr, "tdee": tdee,
        "target_calories": round(target_calories, 1),
        "target_protein_g": target_protein_g,
        "target_carbs_g": target_carbs_g,
        "target_fat_g": target_fat_g,
        "target_fiber_g": target_fiber_g,
        "target_omega3_g": target_omega3_g,
    }


DIET_ALLOWED = {
    "Vegetarian": {"Vegetarian", "Vegan"},
    "Vegan": {"Vegan"},
    "Eggetarian": {"Vegetarian", "Vegan", "Eggetarian"},
    "Non-Vegetarian": {"Vegetarian", "Vegan", "Eggetarian", "Non-Vegetarian"},
}

ALLERGY_CATEGORY_KEYWORDS = {
    "Milk": ["milk"],
    "Nuts": ["nuts & oilseeds"],
    "Fish": ["fish"],
    "Gluten": ["wheat", "barley"],
}

REGION_FIELD = {
    "Mountain": "region_mountain",
    "Hills": "region_hills",
    "Terai": "region_terai",
}


def allowed_foods_for(profile) -> list:
    """Applies diet/allergy/region/availability filters, then the Decision
    Tree medical filter. Returns a plain list of Food instances."""
    qs = Food.objects.filter(available_year_round=True)

    region_field = REGION_FIELD.get(profile.region)
    if region_field:
        qs = qs.filter(**{region_field: True})

    diet_tags = DIET_ALLOWED.get(profile.food_preference, DIET_ALLOWED["Non-Vegetarian"])
    qs = qs.filter(diet_tag__in=diet_tags)

    foods = list(qs)

    # allergy: exclude by category/name keyword
    allergies = [a.strip() for a in (profile.allergies or "").split(",") if a.strip()]
    for allergy in allergies:
        keywords = ALLERGY_CATEGORY_KEYWORDS.get(allergy, [allergy.lower()])
        foods = [
            f for f in foods
            if not any(kw in f.category.lower() or kw in f.name.lower() for kw in keywords)
        ]

    # medical conditions -> Decision Tree
    conditions = [c.strip() for c in (profile.medical_conditions or "").split(",") if c.strip()]
    foods = decision_tree.allowed_foods_for(foods, conditions)

    return foods
