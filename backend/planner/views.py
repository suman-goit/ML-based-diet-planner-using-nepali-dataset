from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .constraint_engine import calculate_targets
from .forms import AssessmentForm
from .meal_generator import generate_meal_plan
from .models import MealPlan, UserProfile
from .serializers import MealPlanSerializer, SignupSerializer, UserProfileSerializer


@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    serializer = SignupSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    user = serializer.save()
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"detail": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    Token.objects.filter(user=request.user).delete()
    return Response({"detail": "Logged out."})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Returns current user + profile (if any) — used by React on app load
    so a saved token can 'remember' the logged-in user."""
    data = {"username": request.user.username, "profile": None}
    try:
        profile = request.user.profile
        data["profile"] = UserProfileSerializer(profile).data
    except UserProfile.DoesNotExist:
        pass
    return Response(data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assessment_view(request):
    """Validates the assessment via a Django Form, runs the Constraint
    Engine to compute BMI/BMR/TDEE + macro targets, and saves the profile."""
    form = AssessmentForm(request.data)
    if not form.is_valid():
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

    cleaned = form.cleaned_data
    try:
        profile = UserProfile.objects.get(user=request.user)
        for field in ["gender", "age", "height_cm", "weight_kg", "activity_level", "goal",
                    "food_preference", "medical_conditions"]:
            setattr(profile, field, cleaned[field])
    except UserProfile.DoesNotExist:
        profile = UserProfile(
            user=request.user,
            gender=cleaned["gender"],
            age=cleaned["age"],
            height_cm=cleaned["height_cm"],
            weight_kg=cleaned["weight_kg"],
            activity_level=cleaned["activity_level"],
            goal=cleaned["goal"],
            food_preference=cleaned["food_preference"],
            medical_conditions=cleaned["medical_conditions"],
        )

    targets = calculate_targets(profile)
    for key, value in targets.items():
        setattr(profile, key, value)

    profile.save()
    return Response(UserProfileSerializer(profile).data, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def generate_plan_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        return Response({"detail": "Complete your health assessment first."}, status=status.HTTP_400_BAD_REQUEST)

    if not profile.target_calories:
        return Response({"detail": "Profile is missing calculated targets."}, status=status.HTTP_400_BAD_REQUEST)

    meal_plan = generate_meal_plan(request.user, profile)
    return Response(MealPlanSerializer(meal_plan).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def latest_plan_view(request):
    plan = MealPlan.objects.filter(user=request.user, is_active=True).order_by("-created_at").first()
    if not plan:
        return Response({"detail": "No meal plan yet."}, status=status.HTTP_404_NOT_FOUND)
    return Response(MealPlanSerializer(plan).data)
