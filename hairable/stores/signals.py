from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WorkCalendar

@receiver(post_save, sender=WorkCalendar)
def update_work_calendar(sender, instance, **kwargs):
    instance.update_store_calendar()