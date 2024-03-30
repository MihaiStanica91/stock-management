from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name=""),
    path("signup", views.signup, name="signup"),
    path("user_logout", views.user_logout, name="user_logout"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("dashboard/company_register", views.company_register, name="company_register"),
]