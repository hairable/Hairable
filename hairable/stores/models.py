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
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_calendar')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='work_calendar')
    date = models.DateField()  # 근무일
    start_time = models.TimeField()  # 근무 시작 시간
    end_time = models.TimeField()  # 근무 종료 시간
    status = models.CharField(max_length=10, choices=[('working', '근무 중'), ('off', '휴무')], default='working')

    class Meta:
        unique_together = ['staff', 'date']  # 특정 직원의 날짜별로 중복 입력 금지

    def clean(self): #주석 : 종료 시간이 시작 시간보다 늦어야 함
        if self.start_time >= self.end_time:
            raise ValidationError("종료 시간은 시작 시간보다 늦어야 합니다.")
        
    def save(self, *args, **kwargs):
        # 직원이 같은 날짜에 이미 등록된 근무 상태가 있을 경우 기존 것을 삭제 후 새로 저장
        WorkCalendar.objects.filter(staff=self.staff, date=self.date).exclude(id=self.id).delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.staff.username} - {self.date} ({self.status})"


class ManagementCalendar(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    date = models.DateField()
    total_working = models.IntegerField(default=0)
    total_off = models.IntegerField(default=0)
    total_substitute = models.IntegerField(default=0) # 대체 근무 인원

    class Meta: # 주석 : 매장과 날짜별로 중복 입력 금지
        unique_together = ['store', 'date']

    def update_calendar(self):
        # 근무 중인 직원과 휴무 중인 직원의 수를 계산하여 캘린더에 반영
        working_count = WorkCalendar.objects.filter(store=self.store, date=self.date, status='working').count()
        off_count = WorkCalendar.objects.filter(store=self.store, date=self.date, status='off').count()

        self.total_staff_working = working_count
        self.total_staff_off = off_count
        self.save()

    def __str__(self): #주석 : 매장 이름과 날짜를 반환
        return f"{self.store.name} - {self.date}"
