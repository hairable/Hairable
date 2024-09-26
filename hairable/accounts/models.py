from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
# Create your models here.


class User(AbstractUser):
    gender_choices = [("M", "남성"), ("F", "여성")]
    username = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=30)
    phoneNumberRegex = RegexValidator(regex = r'^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})')#한국표준, (r"^\+?1?\d{8,15}$ 국제표준)
    phone = models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = True)
    birthday =  models.DateField()
    gender = models.CharField(
        max_length=1, choices=gender_choices, null=True, blank=True
    )
    introduction = models.TextField(null=True, blank=True)

