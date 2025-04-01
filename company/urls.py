from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('register/', views.company_register, name='company_register'),
    path('edit/', views.edit_company, name='edit_company'),
    path('supplier/register/', views.supplier_register, name='supplier_register'),
    path('supplier/list/', views.supplier_list, name='supplier_list'),
] 