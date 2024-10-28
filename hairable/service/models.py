from django.db import models
from inventory.models import InventoryItem
from stores.models import StoreStaff, Category, Store  # 직원 및 카테고리 모델 가져오기
from datetime import timedelta
import datetime
from model_utils import FieldTracker
# 모델 정의

# 서비스-inventory, 서비스-staff 연결을 위한 중간 모델 정의
class ServiceInventory(models.Model):
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

class ServiceDesigner(models.Model):
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    designer = models.ForeignKey('stores.StoreStaff', on_delete=models.CASCADE)
    store = models.ForeignKey('stores.Store', on_delete=models.CASCADE)

# 서비스 모델
class Service(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, help_text="서비스의 카테고리")
    name = models.CharField(max_length=100)  # 서비스 이름
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 서비스 가격
    duration = models.DurationField()  # 서비스 소요 시간
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)  # 서비스가 제공되는 매장 (nullable)
    available_designers = models.ManyToManyField(
        'stores.StoreStaff',
        related_name='designer_services'  # 이 서비스를 제공할 수 있는 디자이너들
    )

    def is_available(self):
        return all(item.inventory_item.is_in_stock(item.quantity) for item in self.serviceinventory_set.all()) and self.available_designers.exists()

# 예약 모델
class Reservation(models.Model):
    """_summary_

    Args:
        models (_type_): _description_
    """
    customer_name = models.CharField(max_length=255, blank=True, null=True, help_text="고객 이름")
    customer_phone_number = models.CharField(max_length=15, blank=True, null=True)
    customer_gender = models.CharField(max_length=1, choices=[('M', '남'), ('F', '여')], blank=True, null=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    reservation_time = models.DateTimeField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    assigned_designer = models.ForeignKey(
    'stores.StoreStaff',
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    limit_choices_to={'role__in': ['designer', 'manager']}
)
    status = models.CharField(max_length=20, choices=[('예약 중', '예약 중'), ('예약 대기', '예약 대기'), ('예약 취소', '예약 취소'), ('방문 완료', '방문 완료')])
    created_at = models.DateTimeField(auto_now_add=True)

    
    tracker = FieldTracker()

    def save(self, *args, **kwargs):
        if not self.pk:  # 새로운 예약인 경우
            if not self.service.store:
                self.service.store = self.assigned_designer.store
                self.service.save()
        elif self.status == '방문 완료' and self.tracker.has_changed('status'):
            self.record_sales()
        super().save(*args, **kwargs)

    def record_sales(self):
        service_price = self.service.price
        inventory_cost = sum(item.inventory_item.cost * item.quantity for item in self.service.serviceinventory_set.all())
        net_profit = service_price - inventory_cost

        report, created = SalesReport.objects.get_or_create(
            store=self.service.store,
            date=self.reservation_time.date(),
            defaults={
                'total_revenue': 0,
                'total_expenses': 0,
                'net_profit': 0,
            }
        )

        if not created:
            # 기존 보고서가 있는 경우, 이전 데이터를 제거
            report.total_revenue -= service_price
            report.total_expenses -= inventory_cost
            report.net_profit -= net_profit

        report.total_revenue += service_price
        report.total_expenses += inventory_cost
        report.net_profit += net_profit
        report.save()
            
    def calculate_profit(self):
        service_price = self.service.price
        inventory_cost = sum(item.inventory_item.cost * item.quantity for item in self.service.serviceinventory_set.all())
        return service_price - inventory_cost

# 고객 모델
class Customer(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    membership_status = models.CharField(max_length=20, choices=[('일반 고객', '일반 고객'), ('멤버십 가입 고객', '멤버십 가입 고객')], default='일반 고객')
    reservation_count = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    is_membership = models.BooleanField(default=False)

# 매출 보고서 모델
class SalesReport(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True)
    date = models.DateField()
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2)
    net_profit = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        unique_together = ('store', 'date')

    @staticmethod
    def generate_report(store, start_date, end_date):
        reservations = Reservation.objects.filter(
            service__store=store,
            reservation_time__date__range=(start_date, end_date)
        )
        total_revenue = sum(reservation.calculate_cost() for reservation in reservations)
        total_expenses = sum(
            item.cost for item in InventoryItem.objects.filter(
                store=store, 
                purchase_date__range=(start_date, end_date)
            )
        )
        total_expenses += sum(
            reservation.assigned_designer.hourly_wage * (reservation.service.duration.total_seconds() / 3600)
            for reservation in reservations if reservation.assigned_designer
        )
        net_profit = total_revenue - total_expenses

        service_sales = {}
        designer_sales = {}
        for reservation in reservations:
            service_name = reservation.service.name
            designer_name = reservation.assigned_designer.user.username if reservation.assigned_designer else 'Unassigned'
            cost = reservation.calculate_cost()
            
            service_sales[service_name] = service_sales.get(service_name, 0) + cost
            designer_sales[designer_name] = designer_sales.get(designer_name, 0) + cost

        return SalesReport(
            store=store,
            date=end_date,
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            net_profit=net_profit,
            service_sales=service_sales,
            designer_sales=designer_sales
        )