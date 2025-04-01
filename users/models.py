from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class CustomUser(models.Model):
    ADMIN = "ADMIN"
    REGULAR_USER = "REGULAR USER"
    ROLE = ((ADMIN, "ADMIN"), 
            (REGULAR_USER, "REGULAR USER"),)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE, default=REGULAR_USER,)

    def is_upperclass(self):
        return self.role in {self.ADMIN, self.REGULAR_USER}

    def __str__(self):
        return self.user.username