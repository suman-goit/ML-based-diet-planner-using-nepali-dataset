from django.contrib.auth.models import User
from rest_framework import serializers

from .models import DayPlan, Food, Meal, MealItem, MealPlan, UserProfile


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)

    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "gender", "age", "height_cm", "weight_kg", "activity_level",
            "goal", "food_preference", "medical_conditions",
            "bmi", "bmr", "tdee",
            "target_calories", "target_protein_g", "target_carbs_g", "target_fat_g",
            "updated_at",
        ]
        read_only_fields = [
            "bmi", "bmr", "tdee", "target_calories",
            "target_protein_g", "target_carbs_g", "target_fat_g", "updated_at",
        ]


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ["id", "name", "description", "calories", "protein_g", "carbs_g", "fat_g", "diet_tag"]


class MealItemSerializer(serializers.ModelSerializer):
    food = FoodSerializer()

    class Meta:
        model = MealItem
        fields = ["id", "food", "servings"]


class MealSerializer(serializers.ModelSerializer):
    items = MealItemSerializer(many=True)
    total_calories = serializers.SerializerMethodField()

    class Meta:
        model = Meal
        fields = ["id", "meal_type", "items", "total_calories"]

    def get_total_calories(self, obj):
        return round(sum(i.servings * i.food.calories for i in obj.items.all()), 1)


class DayPlanSerializer(serializers.ModelSerializer):
    meals = MealSerializer(many=True)

    class Meta:
        model = DayPlan
        fields = ["id", "day_number", "meals"]


class MealPlanSerializer(serializers.ModelSerializer):
    days = DayPlanSerializer(many=True)

    class Meta:
        model = MealPlan
        fields = ["id", "created_at", "target_calories", "days"]
