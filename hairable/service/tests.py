from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Service, Reservation, Customer, Category
from stores.models import Store, StoreStaff
from accounts.models import User
from datetime import date, datetime, timedelta
from django.utils import timezone

class ReservationTests(TestCase):
    def setUp(self):
        # 테스트를 위한 초기 데이터 설정
        self.client = APIClient()
        
        self.ceo = User.objects.create_user(
            username="testceo",
            password="password",
            birthday=date(1990, 1, 1),
            phone="010-1111-1111"  # 고유한 전화번호 설정
        )

        # Store 인스턴스를 생성할 때 ceo 필드 추가
        self.store = Store.objects.create(
            name="Test Store",
            address="123 Test St",
            ceo=self.ceo
        )
        
        # 유저 및 직원 생성
        self.user = User.objects.create_user(
            username='staffuser',
            password='testpassword',
            birthday=date(1995, 5, 15),
            phone="010-2222-2222"  # 고유한 전화번호 설정
        )
        self.staff = StoreStaff.objects.create(store=self.store, user=self.user, role='designer')
        
        # 카테고리 생성
        self.category = Category.objects.create(name="헤어 서비스")

        # 서비스 생성
        self.service = Service.objects.create(
            name="Hair Cut",
            price=30.0,
            duration=timedelta(hours=1),  # timedelta 객체 사용
            store=self.store,
            category=self.category  # 카테고리 추가
        )
        
        # 고객 생성
        self.customer_data = {
            "name": "홍길동",
            "phone_number": "010-1234-5678",
            "gender": "M"
        }
        self.customer = Customer.objects.create(**self.customer_data)
        
        # 예약 데이터
        self.reservation_data = {
            "store_id": self.store.id,
            "customer_name": self.customer_data['name'],
            "customer_phone_number": self.customer_data['phone_number'],
            "customer_gender": self.customer_data['gender'],
            "reservation_time": datetime(2024, 10, 10, 14, 0, tzinfo=timezone.utc),
            "service": self.service.id,
            "assigned_designer": self.staff.id,
            "status": "예약 중"
        }
        # 인증 설정
        self.client.force_authenticate(user=self.ceo)

    def test_create_reservation_successful(self):
        # 정상적인 예약 생성 테스트
        response = self.client.post(reverse('service:reservation-list'), data=self.reservation_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reservation.objects.count(), 1)
        reservation = Reservation.objects.first()
        self.assertEqual(reservation.customer_name, self.customer_data['name'])
        self.assertEqual(reservation.customer_phone_number, self.customer_data['phone_number'])
        self.assertEqual(reservation.customer_gender, self.customer_data['gender'])

    def test_create_reservation_missing_required_field(self):
        # 필수 필드 누락 테스트 (예: customer_name)
        invalid_data = self.reservation_data.copy()
        invalid_data.pop('customer_name')
        response = self.client.post(reverse('service:reservation-list'), data=invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_reservation_invalid_designer(self):
        # 잘못된 디자이너 (다른 매장에 속한 디자이너) 테스트
        another_store = Store.objects.create(name="Another Store", address="456 Another St", ceo=self.ceo)
        another_user = User.objects.create_user(
            username='anotherstaff',
            password='testpassword',
            birthday=date(1993, 3, 3),
            phone="010-3333-3333"
        )
        another_staff = StoreStaff.objects.create(store=another_store, user=another_user, role='designer')

        invalid_data = self.reservation_data.copy()
        invalid_data['assigned_designer'] = another_staff.id
        response = self.client.post(reverse('service:reservation-list'), data=invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("The assigned designer must be from the same store as the service.", str(response.data))
