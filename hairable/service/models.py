from django.db import models
from inventory.models import InventoryItem
from stores.models import StoreStaff, Category  # 직원 및 카테고리 모델 가져오기
from datetime import timedelta
import datetime

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
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()
    available_designers = models.ManyToManyField(
        'stores.StoreStaff', 
        related_name='designer_services'
    )

    def is_available(self):
        return all(item.inventory_item.is_in_stock(item.quantity) for item in self.serviceinventory_set.all()) and self.available_designer is not None

# 예약 모델
class Reservation(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    reservation_time = models.DateTimeField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    assigned_designer = models.ForeignKey('stores.StoreStaff', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'designer'})
    status = models.CharField(max_length=20, choices=[('예약 중', '예약 중'), ('예약 대기', '예약 대기'), ('방문 완료', '방문 완료')])
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_cost(self):
        # Calculate cost based on service price, designer wage, and inventory usage
        designer_cost = self.assigned_designer.hourly_wage * (self.service.duration.total_seconds() / 3600) if self.assigned_designer else 0
        inventory_cost = sum(item.inventory_item.cost * item.quantity for item in self.service.serviceinventory_set.all())
        return self.service.price + designer_cost + inventory_cost


# 고객 모델
class Customer(models.Model):
    name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    membership_status = models.CharField(max_length=20, choices=[('일반 고객', '일반 고객'), ('멤버십 가입 고객', '멤버십 가입 고객')], default='일반 고객')
    reservation_count = models.IntegerField(default=0)
    notes = models.TextField(blank=True)

# 매출 보고서 모델
class SalesReport(models.Model):
    date = models.DateField()
    total_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = models.DecimalField(max_digits=15, decimal_places=2)
    net_profit = models.DecimalField(max_digits=15, decimal_places=2)

    @staticmethod
    def generate_report(start_date, end_date):
        reservations = Reservation.objects.filter(reservation_time__range=(start_date, end_date))
        total_revenue = sum(reservation.calculate_cost() for reservation in reservations)
        total_expenses = sum(item.cost for item in InventoryItem.objects.filter(purchase_date__range=(start_date, end_date)))
        total_expenses += sum(
            reservation.assigned_designer.hourly_wage * (reservation.service.duration.total_seconds() / 3600)
            for reservation in reservations if reservation.assigned_designer
        )
        net_profit = total_revenue - total_expenses
        return SalesReport(date=end_date, total_revenue=total_revenue, total_expenses=total_expenses, net_profit=net_profit)
