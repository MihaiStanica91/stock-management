from django.shortcuts import render, redirect
from django.urls import reverse
from ..forms import LoginForm, SignUpForm, CustomUser, EmailForm, UserEditForm
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from invitations.models import Invitation
from django.contrib import messages


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


    context = {'loginform' : form}

    return render(request, "home.html", context = context)


@login_required(login_url="/")
def dashboard(request):

    return render(request, "dashboard.html")


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
def send_invitation(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            invitation = Invitation.create(
                email=email, 
                inviter=request.user,
            )

            invitation.send_invitation(request)
        return render(request, 'invitation_sent.html')
    else:
        form = EmailForm()

    context = {'invitationform' : form}
    return render(request, 'send_invitation_form.html', context = context)
    

def accept_invitation(key):
    invitation = Invitation.objects.get(key=key)
    invitation.accepted = True
    invitation.save()
    return redirect(reverse("signup"))


@login_required(login_url="/")
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password']
            if password:
                user.set_password(password)
            user.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'edit_profile.html', {'edit_profile': form})