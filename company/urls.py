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
    path('measurement/register/', views.measurement_register, name='measurement_register'),
    path('measurement/list/', views.measurement_list, name='measurement_list'),
    path('measurement/delete/confirm/', views.delete_measurement_confirm, name='delete_measurement_confirm'),
    path('measurement/delete/', views.delete_measurement, name='delete_measurement'),
    path('product/category/register/', views.product_category_register, name='product_category_register'),
    path('product/category/list/', views.product_category_list, name='product_category_list'),
    path('product/category/delete/confirm/', views.delete_product_category_confirm, name='delete_product_category_confirm'),
    path('product/category/delete/', views.delete_product_category, name='delete_product_category'),
    path('vat-rate/register/', views.vat_rate_register, name='vat_rate_register'),
    path('vat-rate/list/', views.vat_rate_list, name='vat_rate_list'),
    path('vat-rate/delete/confirm/', views.delete_vat_rate_confirm, name='delete_vat_rate_confirm'),
    path('vat-rate/delete/', views.delete_vat_rate, name='delete_vat_rate'),
]