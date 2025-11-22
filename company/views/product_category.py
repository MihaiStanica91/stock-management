from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Company, ProductCategory
from ..forms import ProductCategoryForm


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

