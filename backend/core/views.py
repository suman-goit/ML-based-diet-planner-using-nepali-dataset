from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from . import constraint_engine, ilp_engine
from .models import DayPlan, Meal, MealItem, MealPlan, UserProfile
from .serializers import (MealPlanSerializer, SignupSerializer,
                           UserProfileSerializer)


# ---------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "username": user.username}, status=201)
    return Response(serializer.errors, status=400)


@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if not user:
        return Response({"detail": "Invalid credentials"}, status=401)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    request.user.auth_token.delete()
    return Response(status=204)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    latest = request.user.profiles.first()
    data = {"username": request.user.username}
    if latest:
        data["latest_profile"] = UserProfileSerializer(latest).data
    return Response(data)


# ---------------------------------------------------------------------
# Assessment
# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_assessment(request):
    serializer = UserProfileSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    profile = serializer.save(user=request.user)
    targets = constraint_engine.calculate_targets(profile)
    for key, value in targets.items():
        setattr(profile, key, value)
    profile.save()

    return Response(UserProfileSerializer(profile).data, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def assessment_latest(request):
    profile = request.user.profiles.first()
    if not profile:
        return Response({"detail": "No assessment yet"}, status=404)
    return Response(UserProfileSerializer(profile).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def assessment_history(request):
    profiles = request.user.profiles.all()[:365]
    return Response(UserProfileSerializer(profiles, many=True).data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def assessment_delete(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk, user=request.user)
    profile.delete()
    return Response(status=204)


# ---------------------------------------------------------------------
# Meal Plan
# ---------------------------------------------------------------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_meal_plan(request):
    profile = request.user.profiles.first()
    if not profile:
        return Response({"detail": "Complete a health assessment first"}, status=400)

    foods = constraint_engine.allowed_foods_for(profile)
    if not foods:
        return Response({"detail": "No foods match your constraints"}, status=400)

    day_targets = {
        "target_calories": profile.target_calories,
        "target_protein_g": profile.target_protein_g,
        "target_carbs_g": profile.target_carbs_g,
        "target_fat_g": profile.target_fat_g,
    }

    request.user.meal_plans.update(is_active=False)
    meal_plan = MealPlan.objects.create(user=request.user, profile=profile, is_active=True)

    for day_number in range(1, 4):  # 3-day plan
        day_plan = DayPlan.objects.create(meal_plan=meal_plan, day_number=day_number)
        plan = ilp_engine.generate_full_plan(foods, day_targets)
        for meal_type, items in plan.items():
            meal = Meal.objects.create(day_plan=day_plan, meal_type=meal_type)
            for item in items:
                MealItem.objects.create(meal=meal, food=item["food"],
                                         servings=item["servings"], grams=item["grams"])

    return Response(MealPlanSerializer(meal_plan).data, status=201)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def meal_plan_latest(request):
    meal_plan = request.user.meal_plans.filter(is_active=True).first()
    if not meal_plan:
        return Response({"detail": "No active meal plan"}, status=404)
    return Response(MealPlanSerializer(meal_plan).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def regenerate_meal(request):
    day_number = request.data.get("day_number")
    meal_type = request.data.get("meal_type")
    meal_plan = request.user.meal_plans.filter(is_active=True).first()
    if not meal_plan:
        return Response({"detail": "No active meal plan"}, status=404)

    day_plan = get_object_or_404(DayPlan, meal_plan=meal_plan, day_number=day_number)
    meal = get_object_or_404(Meal, day_plan=day_plan, meal_type=meal_type)

    profile = meal_plan.profile
    foods = constraint_engine.allowed_foods_for(profile)
    exclude_ids = set(meal.items.values_list("food_id", flat=True))

    day_targets = {
        "target_calories": profile.target_calories,
        "target_protein_g": profile.target_protein_g,
        "target_carbs_g": profile.target_carbs_g,
        "target_fat_g": profile.target_fat_g,
    }
    new_items = ilp_engine.solve_meal(foods, day_targets, meal_type, exclude_food_ids=exclude_ids)

    meal.items.all().delete()
    for item in new_items:
        MealItem.objects.create(meal=meal, food=item["food"],
                                 servings=item["servings"], grams=item["grams"])

    from .serializers import DayPlanSerializer
    return Response(DayPlanSerializer(day_plan).data)
