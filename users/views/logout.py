from django.shortcuts import redirect
from django.contrib.auth.models import auth

def user_logout(request):

    auth.logout(request)

    return redirect("/")
