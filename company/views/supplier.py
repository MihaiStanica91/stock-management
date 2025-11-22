from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from company.utils import markdownify
from ..models import Company, Supplier
from ..forms import SupplierForm, SupplierEditForm


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

