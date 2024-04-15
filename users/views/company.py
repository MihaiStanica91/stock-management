from django.shortcuts import render, redirect
from ..forms import CompanyForm, CompanyEditForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Company


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

            return redirect("/dashboard")
    
    context = {'company_form':form}
    return render(request, "company_register.html", context = context)


@login_required(login_url="/")
def edit_company(request):
    try:
        company = Company.objects.get(user_id=request.user.id)
    except Company.DoesNotExist:
        # Handle the case where the user does not have a company
        # Check if the message is already in messages
        if not messages.get_messages(request):
            # Add the message only if it's not already in messages
            messages.error(request, 'You do not have a company profile.')
        return redirect('dashboard')  # Redirect to home page or appropriate URL

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
    return render(request, 'edit_company.html', {'edit_company_details': form})