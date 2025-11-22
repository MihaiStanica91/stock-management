from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from ..models import Company, Supplier, ProductCategory, ProductMeasurement, VatRate, Product
from ..forms import ProductForm


@login_required(login_url="/")
def product_register(request):
    form = ProductForm(user=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, user=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Product has been registered successfully!')
            return redirect('company:product_list')
    
    context = {'product_form':form}
    return render(request, "product/product_register.html", context=context)

@login_required(login_url="/")
def edit_product(request):
    # Get all products for the current user's companies
    products = Product.objects.filter(company_id__user_id=request.user.id)
    
    if not products.exists():
        messages.error(request, 'You do not have any products.')
        return redirect('dashboard')
    
    # Get the product_id from POST or GET
    product_id = request.POST.get('product_id') or request.GET.get('product_id')
    
    if not product_id:
        messages.error(request, 'No product selected for editing.')
        return redirect('company:product_list')
    
    try:
        product = products.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, 'Selected product does not exist.')
        return redirect('company:product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product profile have been updated successfully!')
            return redirect('company:product_list')
        else:
            messages.error(request, 'Please correct the errors below.')
            print(form.errors)  # Add this for debugging
    else:
        form = ProductForm(instance=product, user=request.user)

    return render(request, 'product/edit_product.html', {
        'edit_product': form,
        'products': products,
        'selected_product': product
    })

@login_required(login_url="/")
def product_list(request):
    # Get all companies for the current user
    companies = Company.objects.filter(user_id=request.user.id)
    
    if not companies.exists():
        messages.error(request, 'You do not have any company profiles.')
        return redirect('dashboard')
    
    # Get all products for the user's companies
    products = Product.objects.filter(company_id__in=companies)

    context = {'products': products}
    return render(request, "product/product_list.html", context=context)

@login_required(login_url="/")
def delete_product(request):
    # Get all products for the current user's companies
    products = Product.objects.filter(company_id__user_id=request.user.id)
    
    if not products.exists():
        messages.error(request, 'You do not have any products.')
        return redirect('dashboard')
    
    # Get the product_id from POST
    product_id = request.POST.get('product_id')
    
    if not product_id:
        messages.error(request, 'No product selected for deletion.')
        return redirect('company:product_list')
    
    try:
        product = products.get(id=product_id)
        product.delete()
        messages.success(request, 'Product successfully deleted!')
    except Product.DoesNotExist:
        messages.error(request, 'Selected product does not exist.')
    
    return redirect('company:product_list')

@login_required(login_url="/")
def delete_product_confirm(request):
    # Get all products for the current user's companies
    products = Product.objects.filter(company_id__user_id=request.user.id)
    
    if not products.exists():
        messages.error(request, 'You do not have any products.')
        return redirect('dashboard')
    
    # Get the product_id from GET
    product_id = request.GET.get('product_id')
    
    if not product_id:
        messages.error(request, 'No product selected for deletion.')
        return redirect('company:product_list')
    
    try:
        product = products.get(id=product_id)
        return render(request, 'product/delete_product_confirm.html', {
            'product': product
        })
    except Product.DoesNotExist:
        messages.error(request, 'Selected product does not exist.')
        return redirect('company:product_list')

@login_required(login_url="/")
def get_company_options(request):
    """AJAX endpoint to get filtered options for a selected company"""
    company_id = request.GET.get('company_id')
    
    if not company_id:
        return JsonResponse({
            'suppliers': [],
            'categories': [],
            'measurements': [],
            'vat_rates': []
        })
    
    try:
        company = Company.objects.filter(user_id=request.user.id, id=company_id).first()
        if not company:
            return JsonResponse({'error': 'Company not found'}, status=404)
        
        return JsonResponse({
            'suppliers': [{'id': s.id, 'name': s.name} for s in Supplier.objects.filter(company_id=company)],
            'categories': [{'id': c.id, 'name': c.category} for c in ProductCategory.objects.filter(company=company)],
            'measurements': [{'id': m.id, 'name': m.type_of_measurement} for m in ProductMeasurement.objects.filter(company_id=company)],
            'vat_rates': [{'id': v.id, 'name': f"{v.vat_rate}%"} for v in VatRate.objects.filter(company=company)]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

