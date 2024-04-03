from django.urls import path
from .views import home, company, logout, sign_up

urlpatterns = [
    path("", home.home_view, name=""),
    path("signup", sign_up.signup, name="signup"),
    path("user_logout", logout.user_logout, name="user_logout"),
    path("dashboard", home.dashboard, name="dashboard"),
    path("dashboard/company_register", company.company_register, name="company_register"),
]