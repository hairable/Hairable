from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    image = models.ImageField(upload_to='profile_images/', default='profile_images/blank.png', blank=True)
    signature_service=models.TextField(null=True, blank=True)
    company_name=models.TextField()