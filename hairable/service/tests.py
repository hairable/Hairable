from django.test import TestCase
from rest_framework.test import APIClient
from .models import Service, Reservation, Customer, Category
from stores.models import Store  # Store 모델 import
from django.contrib.auth.models import User

class ServiceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Test Category")
        self.store = Store.objects.create(name="Test Store")  # Store 인스턴스 생성
        self.service_data = {
            "category": self.category.id,
            "name": "Test Service",
            "price": 100,
            "duration": 60,
            "store": self.store.id
        }
        self.service = Service.objects.create(**self.service_data)

    def test_create_service(self):
        response = self.client.post('/services/', self.service_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Service.objects.count(), 2)

    def test_get_service(self):
        response = self.client.get(f'/services/{self.service.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.service.name)

    def test_update_service(self):
        updated_data = self.service_data.copy()
        updated_data['name'] = 'Updated Service'
        response = self.client.put(f'/services/{self.service.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.service.refresh_from_db()
        self.assertEqual(self.service.name, 'Updated Service')

    def test_delete_service(self):
        response = self.client.delete(f'/services/{self.service.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Service.objects.count(), 0)

class ReservationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Test Category")
        self.store = Store.objects.create(name="Test Store")  # Store 인스턴스 생성
        self.service = Service.objects.create(category=self.category, name="Test Service", price=100, duration=60, store=self.store)
        self.customer = Customer.objects.create(name="Test Customer", phone_number="010-1234-5678", gender="M")
        self.reservation_data = {
            "customer": self.customer.id,
            "service": self.service.id,
            "assigned_designer": None,
            "status": "예약 대기"
        }
        self.reservation = Reservation.objects.create(**self.reservation_data)

    def test_create_reservation(self):
        response = self.client.post('/reservations/', self.reservation_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Reservation.objects.count(), 2)

    def test_get_reservation(self):
        response = self.client.get(f'/reservations/{self.reservation.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], self.reservation.status)

    def test_update_reservation(self):
        updated_data = self.reservation_data.copy()
        updated_data['status'] = '예약 중'
        response = self.client.put(f'/reservations/{self.reservation.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, '예약 중')

    def test_delete_reservation(self):
        response = self.client.delete(f'/reservations/{self.reservation.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Reservation.objects.count(), 0)

class CustomerTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.customer_data = {
            "name": "Test Customer",
            "phone_number": "010-1234-5678",
            "gender": "M"
        }
        self.customer = Customer.objects.create(**self.customer_data)

    def test_create_customer(self):
        response = self.client.post('/customers/', self.customer_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Customer.objects.count(), 2)

    def test_get_customer(self):
        response = self.client.get(f'/customers/{self.customer.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.customer.name)

    def test_update_customer(self):
        updated_data = self.customer_data.copy()
        updated_data['name'] = 'Updated Customer'
        response = self.client.put(f'/customers/{self.customer.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.name, 'Updated Customer')

    def test_delete_customer(self):
        response = self.client.delete(f'/customers/{self.customer.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Customer.objects.count(), 0)

class CategoryTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_authenticate(user=self.user)
        self.category_data = {
            "name": "Test Category"
        }
        self.category = Category.objects.create(**self.category_data)

    def test_create_category(self):
        response = self.client.post('/categories/', self.category_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Category.objects.count(), 2)

    def test_get_category(self):
        response = self.client.get(f'/categories/{self.category.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.category.name)

    def test_update_category(self):
        updated_data = self.category_data.copy()
        updated_data['name'] = 'Updated Category'
        response = self.client.put(f'/categories/{self.category.id}/', updated_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Category')

    def test_delete_category(self):
        response = self.client.delete(f'/categories/{self.category.id}/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Category.objects.count(), 0)
