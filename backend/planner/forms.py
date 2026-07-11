from django import forms

from .models import UserProfile


class AssessmentForm(forms.Form):
    """Plain Django Form used to validate the health-assessment payload
    coming from the React frontend before it touches the DB / engines."""

    gender = forms.ChoiceField(choices=UserProfile.GENDER_CHOICES)
    age = forms.IntegerField(min_value=1, max_value=120)
    height_cm = forms.FloatField(min_value=50, max_value=300)
    weight_kg = forms.FloatField(min_value=10, max_value=400)
    activity_level = forms.ChoiceField(choices=UserProfile.ACTIVITY_CHOICES)
    goal = forms.ChoiceField(choices=UserProfile.GOAL_CHOICES)
    food_preference = forms.ChoiceField(choices=UserProfile.FOOD_PREF_CHOICES)
    medical_conditions = forms.CharField(required=False, max_length=255)
