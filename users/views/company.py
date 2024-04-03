from django.shortcuts import render, redirect
from ..forms import CompanyForm
from django.contrib.auth.decorators import login_required


def company_register(request):

    form = CompanyForm()

    if request.method == "POST":

        form = CompanyForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("/dashboard")
    
    context = {'companyform':form}
    return render(request, "company_register.html", context = context)


@login_required(login_url="/")
def company_register_url(request):

    return render(request, "company_register.html")