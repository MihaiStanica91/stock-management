from django.shortcuts import render, redirect
from ..models import Company
from ..forms import SupplierForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required(login_url="/")
def supplier_create(request):
    form = SupplierForm()    

    if request.method == 'POST':
        form = SupplierForm(request.POST)

        if form.is_valid():
            try:
                company = Company.objects.get(user_id=request.user.id)
                supplier = form.save(commit=False) 
                supplier.company_id = company 
                supplier.save()  
                return redirect("/dashboard")
            except Company.DoesNotExist:
                # Handle the case where the user doesn't have a company
                if not messages.get_messages(request):
                # Add the message only if it's not already in messages
                    messages.error(request, 'You do not have a registered company.')
                
    
    context = {'supplier_form': form}
    return render(request, 'supplier_register.html', context = context)