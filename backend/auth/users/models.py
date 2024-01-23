from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    number = models.CharField(max_length=255, default = '00000000000')
    metamask_address = models.CharField(max_length=255, unique=True, default='0x0000000000000000000000000000000000000000')
    iin = models.CharField(max_length=12, unique=True, default='000000000000')
    isAdmin = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Contract(models.Model):
    contract_address = models.CharField(max_length=255, unique=True)

class UserRegistration(models.Model):
    iin = models.CharField(max_length=12, unique=True)
    metamask_address = models.CharField(max_length=255, unique=True)
    is_registered = models.BooleanField(default=False)