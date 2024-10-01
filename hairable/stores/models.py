from django.db import models
from accounts.models import User

class Store(models.Model):
    name = models.CharField(max_length=100, unique=True)
    ceo = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stores')
    staff = models.ManyToManyField(User, through='StoreStaff')

    def __str__(self):
        return self.name

class StoreStaff(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role_choices = (
        ('designer', '디자이너'),
        ('manager', '매니저'),
    )
    role = models.CharField(max_length=50, choices=role_choices)

    def __str__(self):
        return f"{self.user.username} - {self.role} in {self.store.name}"
