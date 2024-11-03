from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError #주석 : 오류 발생 시 추가

User = get_user_model()

class Store(models.Model):
    name = models.CharField(max_length=255, unique=True)
    ceo = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stores')
    address = models.CharField(max_length=255, default='unknown')
    
    def __str__(self):
        return self.name


class StoreStaff(models.Model):
    STORE_ROLES = (
        ('designer', 'Designer'),
        ('manager', 'Manager'),
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_staff')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_roles')  # `user` 필드로 통합
    role = models.CharField(max_length=10, choices=STORE_ROLES)
    phone = models.CharField(max_length=16, null=True, blank=True)
    date_joined = models.DateField(auto_now_add=True)
    available_services = models.ManyToManyField('service.Service', related_name='staff_available_services') # 가능한 서비스 
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['store', 'user'], name='unique_store_user')
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.store.name}"


# 서비스 카테고리
class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class WorkCalendar(models.Model):
    staff = models.ForeignKey(StoreStaff, on_delete=models.CASCADE, related_name='work_calendar')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='work_calendar')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=[('working', '근무 중'), ('off', '휴무')], default='working')

    class Meta:
        unique_together = ['store', 'staff', 'date']

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("종료 시간은 시작 시간보다 늦어야 합니다.")
    
    def save(self, *args, **kwargs):
        # 저장하기 전에 해당 직원이 실제로 이 스토어에 속해있는지 확인
        if not StoreStaff.objects.filter(store=self.store, user_id=self.staff.user_id).exists():
            raise ValidationError("이 직원은 해당 스토어에 속해있지 않습니다.")
        
        super().save(*args, **kwargs)
        
        # 저장 후 store_calendar 정보 업데이트
        from django.db.models import Count
        store_calendar = WorkCalendar.objects.filter(store=self.store, date=self.date).aggregate(
            total_working=Count('id', filter=models.Q(status='working')),
            total_off=Count('id', filter=models.Q(status='off'))
        )

    def __str__(self):
        return f"{self.staff.user.username} - {self.date} ({self.status})"