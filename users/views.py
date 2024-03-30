from django.shortcuts import render, redirect
from . forms import SignUpForm, LoginForm, CompanyForm, CustomUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout



def home_view(request):

    form = LoginForm()

    if request.method == 'POST':

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:

                auth.login(request, user)

                return redirect("dashboard")


    context = {'loginform':form}

    return render(request, "home.html", context = context)


def signup(request):

    form = SignUpForm()
    role_form = CustomUser()

    if request.method == "POST":

        form = SignUpForm(request.POST)
        role_form = CustomUser(request.POST)

        if form.is_valid() and role_form.is_valid():

            user = form.save()

            role = role_form.save(commit=False)
            role.user = user

            role.save()

            return redirect("/")
    
    context = {'registerform' : form, 'roleform' : role_form}
    return render(request, "signup.html", context = context)


def user_logout(request):

    auth.logout(request)

    return redirect("/")


@login_required(login_url="/")
def dashboard(request):

    return render(request, "dashboard.html")


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
