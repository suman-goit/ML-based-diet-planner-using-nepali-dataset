from django.contrib import admin

from .models import DayPlan, Food, Meal, MealItem, MealPlan, UserProfile


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ["name", "calories", "protein_g", "carbs_g", "fat_g", "diet_tag", "suitable_meals"]
    search_fields = ["name"]
    list_filter = ["diet_tag"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "bmi", "bmr", "tdee", "target_calories", "goal"]


admin.site.register(MealPlan)
admin.site.register(DayPlan)
admin.site.register(Meal)
admin.site.register(MealItem)
