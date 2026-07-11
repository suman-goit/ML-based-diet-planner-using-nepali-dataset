"""
Meal Planner Generator
=======================
Orchestrates: Constraint Engine (rules + filtering) -> ILP Engine (optimal
serving selection) -> persists a 3-day MealPlan in the database.
"""

from django.db import transaction

from .constraint_engine import allowed_foods_for, meal_calorie_targets
from .ilp_engine import solve_meal
from .models import DayPlan, Meal, MealItem, MealPlan

DAYS = 3
MEAL_TYPES = ["breakfast", "lunch", "dinner"]


@transaction.atomic
def generate_meal_plan(user, profile) -> MealPlan:
    """Builds and saves a fresh 3-day meal plan for the given user/profile."""

    # deactivate previous plans so the frontend only shows the latest
    MealPlan.objects.filter(user=user, is_active=True).update(is_active=False)

    meal_plan = MealPlan.objects.create(user=user, target_calories=profile.target_calories)

    cal_targets = meal_calorie_targets(profile.target_calories)
    protein_per_meal = profile.target_protein_g / 3
    carbs_per_meal = profile.target_carbs_g / 3
    fat_per_meal = profile.target_fat_g / 3

    for day_number in range(1, DAYS + 1):
        day_plan = DayPlan.objects.create(meal_plan=meal_plan, day_number=day_number)

        for meal_type in MEAL_TYPES:
            legal_foods = list(allowed_foods_for(profile, meal_type))
            selection = solve_meal(
                foods=legal_foods,
                calorie_target=cal_targets[meal_type],
                protein_target=protein_per_meal,
                carbs_target=carbs_per_meal,
                fat_target=fat_per_meal,
            )

            meal = Meal.objects.create(day_plan=day_plan, meal_type=meal_type)
            for food, servings in selection:
                MealItem.objects.create(meal=meal, food=food, servings=servings)

    return meal_plan
