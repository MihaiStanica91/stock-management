from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Company, VatRate
from ..forms import VatRateForm


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

