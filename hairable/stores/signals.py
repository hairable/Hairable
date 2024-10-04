from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WorkCalendar, ManagementCalendar

# WorkCalendar에 변화가 생길 때 자동으로 ManagementCalendar를 업데이트하는 시그널
@receiver(post_save, sender=WorkCalendar)
def update_management_calendar(sender, instance, **kwargs):
    store = instance.store
    date = instance.date

    management_calendar, created = ManagementCalendar.objects.get_or_create(store=store, date=date)

    # 근무 중인 직원, 휴무 중인 직원, 대타 직원 수 계산
    total_working = WorkCalendar.objects.filter(store=store, date=date, status='working').count()
    total_off = WorkCalendar.objects.filter(store=store, date=date, status='off').count()

    # ManagementCalendar 업데이트 (필요시 대타 인원 로직 추가 가능)
    management_calendar.total_working = total_working
    management_calendar.total_off = total_off
    management_calendar.save()
