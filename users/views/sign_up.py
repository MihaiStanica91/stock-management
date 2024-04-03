from django.shortcuts import render, redirect
from ..forms import SignUpForm, CustomUser


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