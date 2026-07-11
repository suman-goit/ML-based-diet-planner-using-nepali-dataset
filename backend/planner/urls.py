from django.urls import path

from . import views

urlpatterns = [
    path("auth/signup/", views.signup_view, name="signup"),
    path("auth/login/", views.login_view, name="login"),
    path("auth/logout/", views.logout_view, name="logout"),
    path("auth/me/", views.me_view, name="me"),

    path("assessment/", views.assessment_view, name="assessment"),
    path("meal-plan/generate/", views.generate_plan_view, name="generate-plan"),
    path("meal-plan/latest/", views.latest_plan_view, name="latest-plan"),
]
