from django.shortcuts import render, redirect
from ..models import Company, Supplier
from ..forms import SupplierForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required(login_url="/")
def supplier_create(request):
    form = SupplierForm(user=request.user)    

    if request.method == 'POST':
        form = SupplierForm(request.POST, user=request.user)

        if form.is_valid():
            try:
                supplier = form.save(commit=False)
                supplier.save()
                messages.success(request, 'Supplier has been created successfully!')
                return redirect("/dashboard")
            except Exception as e:
                messages.error(request, 'An error occurred while creating the supplier.')
                
    context = {'supplier_form': form}
    return render(request, 'supplier_register.html', context = context)

@login_required(login_url="/")
def supplier_list(request):
    try:
        # Get all companies where the user is associated
        user_companies = Company.objects.filter(user_id=request.user.id)
        if user_companies.exists():
            # Get all suppliers from these companies
            suppliers = Supplier.objects.filter(company_id__in=user_companies)
            return render(request, 'supplier_list.html', {'suppliers': suppliers})
        else:
            messages.error(request, 'You do not have any registered companies.')
            return redirect('/dashboard')
    except Exception as e:
        messages.error(request, 'An error occurred while fetching suppliers.')
        return redirect('/dashboard')