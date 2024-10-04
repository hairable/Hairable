from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Store(models.Model):
    name = models.CharField(max_length=255, unique=True)
    ceo = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stores')

    def __str__(self):
        return self.name


class StoreStaff(models.Model):
    STORE_ROLES = (
        ('designer', 'Designer'),
        ('manager', 'Manager'),
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='store_staff')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='staff_roles')
    role = models.CharField(max_length=10, choices=STORE_ROLES)
    phone = models.CharField(max_length=16, null=True, blank=True)
    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.store.name}"


class WorkCalendar(models.Model):
    staff = models.ForeignKey(User, on_delete=models.CASCADE, related_name='work_calendar')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='work_calendar')
    date = models.DateField()  # 근무일
    start_time = models.TimeField()  # 근무 시작 시간
    end_time = models.TimeField()  # 근무 종료 시간
    status = models.CharField(max_length=10, choices=[('working', '근무 중'), ('off', '휴무')], default='working')

    class Meta:
        unique_together = ['staff', 'date']  # 특정 직원의 날짜별로 중복 입력 금지

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
    

    def update_calendar(self):
        # 근무 중인 직원과 휴무 중인 직원의 수를 계산하여 캘린더에 반영
        working_count = WorkCalendar.objects.filter(store=self.store, date=self.date, status='working').count()
        off_count = WorkCalendar.objects.filter(store=self.store, date=self.date, status='off').count()

        self.total_staff_working = working_count
        self.total_staff_off = off_count
        self.save()
