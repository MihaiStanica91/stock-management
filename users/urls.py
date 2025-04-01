from django.urls import path
from .views import user

urlpatterns = [
    path("", user.home_view, name=""),
    path("signup", user.signup, name="signup"),
    path("user-logout", user.user_logout, name="user_logout"),
    path("dashboard", user.dashboard, name="dashboard"),
    path("dashboard/send-invitation-form", user.send_invitation, name="send_invitation_form"),
    path('accept-invite/<str:key>/', user.accept_invitation, name='accept_invite'),
    path("dashboard/edit-profile", user.edit_profile, name="edit_profile"),
]