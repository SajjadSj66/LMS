from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# User Model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('borrower', 'Borrower'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='borrower')

    def __str__(self):
        return self.username

class Borrower(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='borrower_profile', blank=True, null=True)
    registration_date = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.user.username