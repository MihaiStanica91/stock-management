from django.urls import path
from .views import company, user

urlpatterns = [
    path("", user.home_view, name=""),
    path("signup", user.signup, name="signup"),
    path("user_logout", user.user_logout, name="user_logout"),
    path("dashboard", user.dashboard, name="dashboard"),
    path("dashboard/company_register", company.company_register, name="company_register"),
    path("dashboard/send_invitation_form", user.send_invitation, name="send_invitation_form"),
    path('accept-invite/<str:key>/', user.accept_invitation, name='accept-invite'),
    path("dashboard/edit_profile", user.edit_profile, name="edit_profile"),
    path("dashboard/edit_company_details", company.edit_company, name="edit_company_details"),
]