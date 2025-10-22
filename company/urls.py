from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('register/', views.company_register, name='company_register'),
    path('edit/', views.edit_company, name='edit_company'),
    path('supplier/register/', views.supplier_register, name='supplier_register'),
    path('supplier/list/', views.supplier_list, name='supplier_list'),
    path('supplier/list/profile', views.supplier_profile, name='supplier_profile'),
    path('supplier/list/edit-supplier', views.edit_supplier, name='edit_supplier'),
    path('supplier/delete/confirm/', views.delete_supplier_confirm, name='delete_supplier_confirm'),
    path('supplier/delete/', views.delete_supplier, name='delete_supplier'),
] 