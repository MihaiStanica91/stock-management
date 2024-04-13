from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Company(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, unique = True)
    address = models.CharField(max_length=200)
    email = models.EmailField(max_length = 100, unique = True)
    phone_number = models.CharField(max_length = 100)
    category = models.CharField(max_length=200)
    created_date = models.DateField(auto_now_add = True)

    def __str__(self):
        return self.name



class CustomUser(models.Model):
    ADMIN = "ADMIN"
    REGULAR_USER = "REGULAR USER"
    ROLE = ((ADMIN, "ADMIN"), 
            (REGULAR_USER, "REGULAR USER"),)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE, default=ADMIN,)

    def is_upperclass(self):
        return self.role in {self.ADMIN, self.REGULAR_USER}

    
    def __str__(self):
        return self.user.username