from django.db import models
from django.contrib.auth.models import User


class Company(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=100)
    category = models.CharField(max_length=200)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

