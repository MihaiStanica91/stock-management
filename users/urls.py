from django.urls import path
from .views import company, user, supplier

urlpatterns = [
    path("", user.home_view, name=""),
    path("signup", user.signup, name="signup"),
    path("user-logout", user.user_logout, name="user_logout"),
    path("dashboard", user.dashboard, name="dashboard"),
    path("dashboard/company-register", company.company_register, name="company_register"),
    path("dashboard/send-invitation-form", user.send_invitation, name="send_invitation_form"),
    path('accept-invite/<str:key>/', user.accept_invitation, name='accept_invite'),
    path("dashboard/edit-profile", user.edit_profile, name="edit_profile"),
    path("dashboard/edit-company-details", company.edit_company, name="edit_company_details"),
    path("dashboard/new_supplier/", supplier.supplier_create, name="supplier_create")
]