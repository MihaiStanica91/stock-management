from django.shortcuts import render, redirect
from . forms import SignUpForm, LoginForm
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

    if request.method == "POST":

        form = SignUpForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect("/")
    
    context = {'registerform':form}
    return render(request, "signup.html", context = context)


def user_logout(request):

    auth.logout(request)

    return redirect("/")


@login_required(login_url="/")
def dashboard(request):

    return render(request, "dashboard.html")