from django.contrib.auth.models import User
from django.db import models


# ---------------------------------------------------------------------------
# User health profile (the "assessment")
# ---------------------------------------------------------------------------
class UserProfile(models.Model):
    GENDER_CHOICES = [("M", "Male"), ("F", "Female")]
    ACTIVITY_CHOICES = [
        ("sedentary", "Sedentary (little/no exercise)"),
        ("light", "Light (1-3 days/week)"),
        ("moderate", "Moderate (3-5 days/week)"),
        ("active", "Active (6-7 days/week)"),
        ("very_active", "Very active (hard exercise/physical job)"),
    ]
    GOAL_CHOICES = [
        ("lose", "Lose Weight"),
        ("maintain", "Maintain Weight"),
        ("gain", "Gain Weight"),
    ]
    FOOD_PREF_CHOICES = [
        ("veg", "Vegetarian"),
        ("nonveg", "Non-Vegetarian"),
        ("vegan", "Vegan"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    age = models.PositiveIntegerField()
    height_cm = models.FloatField(help_text="Height in centimetres")
    weight_kg = models.FloatField(help_text="Weight in kilograms")
    activity_level = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    goal = models.CharField(max_length=10, choices=GOAL_CHOICES)
    food_preference = models.CharField(max_length=10, choices=FOOD_PREF_CHOICES)

    # Medical conditions stored as a simple comma-separated tag list, e.g.
    # "diabetes,hypertension". Kept simple on purpose for the prototype.
    medical_conditions = models.CharField(max_length=255, blank=True, default="")

    # Calculated & cached fields (recomputed every time the assessment runs)
    bmi = models.FloatField(null=True, blank=True)
    bmr = models.FloatField(null=True, blank=True)
    tdee = models.FloatField(null=True, blank=True)
    target_calories = models.FloatField(null=True, blank=True)
    target_protein_g = models.FloatField(null=True, blank=True)
    target_carbs_g = models.FloatField(null=True, blank=True)
    target_fat_g = models.FloatField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def medical_conditions_list(self):
        return [c.strip() for c in self.medical_conditions.split(",") if c.strip()]

    def __str__(self):
        return f"Profile({self.user.username})"


# ---------------------------------------------------------------------------
# Nepali food database
# ---------------------------------------------------------------------------
class Food(models.Model):
    MEAL_TYPES = [("breakfast", "Breakfast"), ("lunch", "Lunch"), ("dinner", "Dinner")]
    DIET_TAGS = [("veg", "Vegetarian"), ("nonveg", "Non-Vegetarian"), ("vegan", "Vegan")]

    name = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True, default="")

    # Nutrition per single serving
    calories = models.FloatField()
    protein_g = models.FloatField()
    carbs_g = models.FloatField()
    fat_g = models.FloatField()
    sugar_g = models.FloatField(default=0)
    sodium_mg = models.FloatField(default=0)

    diet_tag = models.CharField(max_length=10, choices=DIET_TAGS, default="veg")
    suitable_meals = models.CharField(
        max_length=60,
        default="breakfast,lunch,dinner",
        help_text="Comma separated subset of breakfast,lunch,dinner",
    )

    # Comma separated medical conditions this food should be EXCLUDED for,
    # e.g. "diabetes,hypertension"
    exclude_for_conditions = models.CharField(max_length=255, blank=True, default="")

    def suitable_meals_list(self):
        return [m.strip() for m in self.suitable_meals.split(",") if m.strip()]

    def exclude_list(self):
        return [c.strip() for c in self.exclude_for_conditions.split(",") if c.strip()]

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Generated meal plan
# ---------------------------------------------------------------------------
class MealPlan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="meal_plans")
    created_at = models.DateTimeField(auto_now_add=True)
    target_calories = models.FloatField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"MealPlan({self.user.username}, {self.created_at:%Y-%m-%d})"


class DayPlan(models.Model):
    meal_plan = models.ForeignKey(MealPlan, on_delete=models.CASCADE, related_name="days")
    day_number = models.PositiveIntegerField()  # 1, 2, 3

    class Meta:
        ordering = ["day_number"]

    def __str__(self):
        return f"Day {self.day_number}"


class Meal(models.Model):
    MEAL_TYPES = [("breakfast", "Breakfast"), ("lunch", "Lunch"), ("dinner", "Dinner")]

    day_plan = models.ForeignKey(DayPlan, on_delete=models.CASCADE, related_name="meals")
    meal_type = models.CharField(max_length=10, choices=MEAL_TYPES)

    class Meta:
        ordering = ["meal_type"]

    def __str__(self):
        return f"{self.day_plan} - {self.meal_type}"


class MealItem(models.Model):
    """A single food item (with serving count) inside a Meal, chosen by the ILP engine."""

    meal = models.ForeignKey(Meal, on_delete=models.CASCADE, related_name="items")
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    servings = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.servings} x {self.food.name}"
