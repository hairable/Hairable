from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings

class User(AbstractUser):
    gender_choices = [("M", "남성"), ("F", "여성")]
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    phoneNumberRegex = RegexValidator(regex=r'^01[016789]-?\d{3,4}-?\d{4}$', message="유효한 한국 전화번호를 입력하세요.")
    phone = models.CharField(validators=[phoneNumberRegex], max_length=16, unique=True)
    birthday = models.DateField()
    gender = models.CharField(max_length=1, choices=gender_choices, null=True, blank=True)
    introduction = models.TextField(null=True, blank=True)
    ROLE_CHOICES = (
        ('CEO', '대표'),
        ('user', '일반회원'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    store = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', default='images/default_imgage.jpg')
    introduction = models.TextField(null=True, blank=True) # 자기소개
    specialty = models.CharField(max_length=100, blank=True, null=True) # 가장 자신있는 시술
    work_status = models.BooleanField(default=True)  # 근무 상태
    career_list = models.JSONField(default=list, blank=True)  # 경력 목록
    certificate_list = models.JSONField(default=list, blank=True)  # 자격증 목록