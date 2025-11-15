from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from company.utils import markdownify
from .models import Company, Supplier, ProductMeasurement, ProductCategory, VatRate
from .forms import CompanyForm, CompanyEditForm, SupplierForm, SupplierEditForm, TypeOfMeasurementForm, ProductCategoryForm, VatRateForm 

# Create your views here.

@login_required(login_url="/")
def company_register(request):
    form = CompanyForm()

    if request.method == "POST":
        form = CompanyForm(request.POST)

        if form.is_valid():
            user = request.user
            company = form.save(commit=False)
            company.user_id = user
            company.save()
            
            messages.success(request, 'Company profile has been created successfully!')
            return redirect("/dashboard")
    
    context = {'company_form':form}
    return render(request, "company/company_register.html", context=context)

@login_required(login_url="/")
def edit_company(request):
    # Get all companies for the current user
    companies = Company.objects.filter(user_id=request.user.id)
    
    if not companies.exists():
        messages.error(request, 'You do not have any company profiles.')
        return redirect('dashboard')

    # If company_id is provided in POST or GET, edit that specific company
    company_id = request.POST.get('company_id') or request.GET.get('company_id')
    
    if company_id:
        try:
            company = companies.get(id=company_id)
        except Company.DoesNotExist:
            messages.error(request, 'Selected company does not exist.')
            return redirect('dashboard')

        if request.method == 'POST':
            form = CompanyEditForm(request.POST, instance=company)
            if form.is_valid():
                form.save()
                messages.success(request, 'Company details have been updated successfully!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Please correct the errors below.')
        else:
            form = CompanyEditForm(instance=company)
        
        return render(request, 'company/edit_company.html', {
            'edit_company_details': form,
            'companies': companies,
            'selected_company': company
        })
    
    # If no company is selected, show the company selection page
    return render(request, 'company/edit_company.html', {
        'companies': companies,
        'show_selection': True
    })

@login_required(login_url="/")
def supplier_register(request):
    form = SupplierForm(user=request.user)

    if request.method == "POST":
        form = SupplierForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier has been registered successfully!')
            return redirect('company:supplier_list')
    
    context = {'supplier_form':form}
    return render(request, "supplier/supplier_register.html", context=context)

@login_required(login_url="/")
def supplier_list(request):
    # Get all companies for the current user
    companies = Company.objects.filter(user_id=request.user.id)
    
    if not companies.exists():
        messages.error(request, 'You do not have any company profiles.')
        return redirect('dashboard')
    
    # Get all suppliers for the user's companies
    suppliers = Supplier.objects.filter(company_id__in=companies)
    
    context = {'suppliers': suppliers}
    return render(request, "supplier/supplier_list.html", context=context)
    
@login_required(login_url="/")
def supplier_profile(request):
    # Get all companies for the current user
    companies = Company.objects.filter(user_id=request.user.id)
    
    if not companies.exists():
        messages.error(request, 'You do not have any company profiles.')
        return redirect('dashboard')
    
    # Get the supplier_id from query parameters
    supplier_id = request.GET.get('supplier_id')
    
    if not supplier_id:
        messages.error(request, 'No supplier selected.')
        return redirect('company:supplier_list')
    
    try:
        # Get the specific supplier for the user's companies
        supplier = Supplier.objects.filter(company_id__in=companies).get(id=supplier_id)
        supplier.description = markdownify(supplier.supplier_details)
        context = {'supplier': supplier}
        return render(request, "supplier/supplier_profile.html", context=context)
        
    except Supplier.DoesNotExist:
        messages.error(request, 'Supplier not found or you do not have permission to view this supplier.')
        return redirect('company:supplier_list')


@login_required(login_url="/")
def edit_supplier(request):
    # Get all suppliers for the current user's companies
    suppliers = Supplier.objects.filter(company_id__user_id=request.user.id)
    
    if not suppliers.exists():
        messages.error(request, 'You do not have any suppliers.')
        return redirect('dashboard')

    # Get the supplier_id from POST or GET
    supplier_id = request.POST.get('supplier_id') or request.GET.get('supplier_id')
    
    try:
        supplier = suppliers.get(id=supplier_id)
    except Supplier.DoesNotExist:
        messages.error(request, 'Selected supplier does not exist.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = SupplierEditForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier profile have been updated successfully!')
            return redirect(f'/company/supplier/list/profile?supplier_id={supplier_id}')
        else:
            messages.error(request, 'Please correct the errors below.')
            print(form.errors)  # Add this for debugging
    else:
        form = SupplierEditForm(instance=supplier)
    
    return render(request, 'supplier/edit_supplier.html', {
        'edit_supplier': form,
        'suppliers': suppliers,
        'selected_supplier': supplier
    })

@login_required(login_url="/")
def delete_supplier_confirm(request):
    # Get all suppliers for the current user's companies
    suppliers = Supplier.objects.filter(company_id__user_id=request.user.id)
    
    if not suppliers.exists():
        messages.error(request, 'You do not have any suppliers.')
        return redirect('dashboard')

    # Get the supplier_id from GET
    supplier_id = request.GET.get('supplier_id')
    
    if not supplier_id:
        messages.error(request, 'No supplier selected for deletion.')
        return redirect('company:supplier_list')
    
    try:
        supplier = suppliers.get(id=supplier_id)
        return render(request, 'supplier/delete_supplier_confirm.html', {
            'supplier': supplier
        })
    except Supplier.DoesNotExist:
        messages.error(request, 'Selected supplier does not exist.')
        return redirect('company:supplier_list')

@login_required(login_url="/")
def delete_supplier(request):
    # Get all suppliers for the current user's companies
    suppliers = Supplier.objects.filter(company_id__user_id=request.user.id)
    
    if not suppliers.exists():
        messages.error(request, 'You do not have any suppliers.')
        return redirect('dashboard')

    # Get the supplier_id from POST
    supplier_id = request.POST.get('supplier_id')
    
    if not supplier_id:
        messages.error(request, 'No supplier selected for deletion.')
        return redirect('company:supplier_list')
    
    try:
        supplier = suppliers.get(id=supplier_id)
        supplier.delete()
        messages.success(request, 'Supplier successfully deleted!')
    except Supplier.DoesNotExist:
        messages.error(request, 'Selected supplier does not exist.')
    
    return redirect('company:supplier_list')

@login_required(login_url="/")
def measurement_register(request):
    form = TypeOfMeasurementForm(user=request.user)

    if request.method == "POST":
        form = TypeOfMeasurementForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Measurement has been registered successfully!')
            return redirect('company:measurement_list')
    
    context = {'type_of_measurement_form':form}
    return render(request, "product/measurement_register.html", context=context)

@login_required(login_url="/")
def measurement_list(request):
    # Get all companies for the current user
    companies = Company.objects.filter(user_id=request.user.id)
    
    if not companies.exists():
        messages.error(request, 'You do not have any company profiles.')
        return redirect('dashboard')
    
    # Get all measurements for the user's companies
    measurements = ProductMeasurement.objects.filter(company_id__in=companies)
    
    context = {'measurements': measurements}
    return render(request, "product/measurement_list.html", context=context)

@login_required(login_url="/")
def delete_measurement(request):
    # Get all measurements for the current user's companies
    measurements = ProductMeasurement.objects.filter(company_id__user_id=request.user.id)
    
    if not measurements.exists():
        messages.error(request, 'You do not have any measurements.')
        return redirect('dashboard')

    # Get the measurement_id from POST
    measurement_id = request.POST.get('measurement_id')
    
    if not measurement_id:
        messages.error(request, 'No measurement selected for deletion.')
        return redirect('company:measurement_list')
    
    try:
        measurement = measurements.get(id=measurement_id)
        measurement.delete()
        messages.success(request, 'Measurement successfully deleted!')
    except ProductMeasurement.DoesNotExist:
        messages.error(request, 'Selected measurement does not exist.')
    
    return redirect('company:measurement_list')

@login_required(login_url="/")
def delete_measurement_confirm(request):
    # Get all measurements for the current user's companies
    measurements = ProductMeasurement.objects.filter(company_id__user_id=request.user.id)
    
    if not measurements.exists():
        messages.error(request, 'You do not have any measurements.')
        return redirect('dashboard')

    # Get the measurement_id from GET
    measurement_id = request.GET.get('measurement_id')
    
    if not measurement_id:
        messages.error(request, 'No measurement selected for deletion.')
        return redirect('company:measurement_list')
    
    try:
        measurement = measurements.get(id=measurement_id)
        return render(request, 'product/delete_measurement_confirm.html', {
            'measurement': measurement
        })
    except ProductMeasurement.DoesNotExist:
        messages.error(request, 'Selected measurement does not exist.')
        return redirect('company:measurement_list')

@login_required(login_url="/")
def product_category_register(request):
    form = ProductCategoryForm(user=request.user)

    if request.method == "POST":
        form = ProductCategoryForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Product category has been registered successfully!')
            return redirect('company:product_category_list')
    
    context = {'product_category_form':form}
    return render(request, "product/product_category_register.html", context=context)

@login_required(login_url="/")
def product_category_list(request):
    # Get all companies for the current user
    companies = Company.objects.filter(user_id=request.user.id)
    
    if not companies.exists():
        messages.error(request, 'You do not have any company profiles.')
        return redirect('dashboard')
    
    # Get all product categories for the user's companies
    product_categories = ProductCategory.objects.filter(company_id__in=companies)

    context = {'product_categories': product_categories}
    return render(request, "product/product_category_list.html", context=context)

@login_required(login_url="/")
def delete_product_category(request):
    # Get all product categories for the current user's companies
    product_categories = ProductCategory.objects.filter(company_id__user_id=request.user.id)
    
    if not product_categories.exists():
        messages.error(request, 'You do not have any product categories.')
        return redirect('dashboard')
    
    # Get the product_category_id from POST
    product_category_id = request.POST.get('product_category_id')
    
    if not product_category_id:
        messages.error(request, 'No product category selected for deletion.')
        return redirect('company:product_category_list')
    
    try:
        product_category = product_categories.get(id=product_category_id)
        product_category.delete()
        messages.success(request, 'Product category successfully deleted!')
    except ProductCategory.DoesNotExist:
        messages.error(request, 'Selected product category does not exist.')
        
    return redirect('company:product_category_list')

@login_required(login_url="/")
def delete_product_category_confirm(request):
    # Get all product categories for the current user's companies
    product_categories = ProductCategory.objects.filter(company_id__user_id=request.user.id)
    
    if not product_categories.exists():
        messages.error(request, 'You do not have any product categories.')
        return redirect('dashboard')
    
    # Get the product_category_id from GET
    product_category_id = request.GET.get('product_category_id')
    
    if not product_category_id:
        messages.error(request, 'No product category selected for deletion.')
        return redirect('company:product_category_list')
    
    try:
        product_category = product_categories.get(id=product_category_id)
        return render(request, 'product/delete_product_category_confirm.html', {
            'product_category': product_category
        })
    except ProductCategory.DoesNotExist:
        messages.error(request, 'Selected product category does not exist.')
        return redirect('company:product_category_list')

@login_required(login_url="/")
def vat_rate_register(request):
    form = VatRateForm(user=request.user)

    if request.method == "POST":
        form = VatRateForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'VAT rate has been registered successfully!')
            return redirect('company:vat_rate_list')
    
    context = {'vat_rate_form':form}
    return render(request, "product/vat_rate_register.html", context=context)

@login_required(login_url="/")
def vat_rate_list(request):
    # Get all companies for the current user
    companies = Company.objects.filter(user_id=request.user.id)
    
    if not companies.exists():
        messages.error(request, 'You do not have any company profiles.')
        return redirect('dashboard')
    
    # Get all VAT rates for the user's companies
    vat_rates = VatRate.objects.filter(company_id__in=companies)

    context = {'vat_rates': vat_rates}
    return render(request, "product/vat_rate_list.html", context=context)

@login_required(login_url="/")
def delete_vat_rate(request):
    # Get all VAT rates for the current user's companies
    vat_rates = VatRate.objects.filter(company_id__user_id=request.user.id)
    
    if not vat_rates.exists():
        messages.error(request, 'You do not have any VAT rates.')
        return redirect('dashboard')
    
    # Get the vat_rate_id from POST
    vat_rate_id = request.POST.get('vat_rate_id')
    
    if not vat_rate_id:
        messages.error(request, 'No VAT rate selected for deletion.')
        return redirect('company:vat_rate_list')
    
    try:
        vat_rate = vat_rates.get(id=vat_rate_id)
        vat_rate.delete()
        messages.success(request, 'VAT rate successfully deleted!')
    except VatRate.DoesNotExist:
        messages.error(request, 'Selected VAT rate does not exist.')
        
    return redirect('company:vat_rate_list')

@login_required(login_url="/")
def delete_vat_rate_confirm(request):
    # Get all VAT rates for the current user's companies
    vat_rates = VatRate.objects.filter(company_id__user_id=request.user.id)
    
    if not vat_rates.exists():
        messages.error(request, 'You do not have any VAT rates.')
        return redirect('dashboard')
    
    # Get the vat_rate_id from GET
    vat_rate_id = request.GET.get('vat_rate_id')
    
    if not vat_rate_id:
        messages.error(request, 'No VAT rate selected for deletion.')
        return redirect('company:vat_rate_list')
    
    try:
        vat_rate = vat_rates.get(id=vat_rate_id)
        return render(request, 'product/delete_vat_rate_confirm.html', {
            'vat_rate': vat_rate
        })
    except VatRate.DoesNotExist:
        messages.error(request, 'Selected VAT rate does not exist.')
        return redirect('company:vat_rate_list')    