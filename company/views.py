from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Company, Supplier
from .forms import CompanyForm, CompanyEditForm, SupplierForm

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
            return redirect("/dashboard")
    
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
