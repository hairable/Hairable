import openai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .config import OPENAI_API_KEY
from service.models import Reservation, Service, SalesReport
from stores.models import Store, StoreStaff
from inventory.models import InventoryItem
from django.db.models import Sum
from datetime import datetime, timedelta
import re
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


openai.api_key = OPENAI_API_KEY

class AIAssistantView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_query = request.data.get("query")
        if not user_query:
            return Response({"error": "질문이 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

        response_content = ""

        if "매출 보고서" in user_query:
            response_content = self.generate_sales_report(user, user_query)
        elif "서비스" in user_query and "제공" in user_query:
            response_content = self.get_store_services(user, user_query)
        elif "예약" in user_query:
            if "조회" in user_query:
                response_content = self.get_reservations(user)
            elif "추가" in user_query:
                response_content = self.add_reservation(user, user_query)
        elif "재고" in user_query:
            response_content = self.get_inventory_info(user)
        elif "직원" in user_query:
            response_content = self.get_staff_info(user)
        else:
            response_content = self.get_ai_response(user, user_query)

        return Response({"response": response_content}, status=status.HTTP_200_OK)

    def generate_sales_report(self, user, query):
        period = re.search(r'(지난|이번|올해)(\s\d+일|\s달)?', query)
        if period:
            period = period.group()
            end_date = datetime.now()
            if "지난" in period:
                days = int(re.search(r'\d+', period).group()) if re.search(r'\d+', period) else 30
                start_date = end_date - timedelta(days=days)
            elif "이번 달" in period:
                start_date = end_date.replace(day=1)
            elif "올해" in period:
                start_date = end_date.replace(month=1, day=1)
        else:
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()

        stores = Store.objects.filter(ceo=user)
        total_revenue = 0
        total_expenses = 0

        for store in stores:
            reservations = Reservation.objects.filter(
                service__store=store,
                reservation_time__range=(start_date, end_date)
            )
            revenue = reservations.aggregate(Sum('service__price'))['service__price__sum'] or 0
            total_revenue += revenue

            expenses = InventoryItem.objects.filter(
                store=store,
                purchase_date__range=(start_date, end_date)
            ).aggregate(Sum('purchase_price'))['purchase_price__sum'] or 0
            total_expenses += expenses

        net_profit = total_revenue - total_expenses

        report = SalesReport.objects.create(
            date=end_date,
            total_revenue=total_revenue,
            total_expenses=total_expenses,
            net_profit=net_profit
        )

        return f"{period} 매출 보고서:\n총 수익: {total_revenue}원\n총 비용: {total_expenses}원\n순이익: {net_profit}원"

    def get_store_services(self, user, query):
        match = re.search(r'(.+?)는 어떤 서비스를 제공', query)
        if match:
            store_name = match.group(1).strip()
            try:
                store = Store.objects.get(name=store_name, ceo=user)
                services = Service.objects.filter(store=store)
                if services.exists():
                    service_names = [service.name for service in services]
                    return f"{store_name}에서 제공하는 서비스는 다음과 같습니다: {', '.join(service_names)}."
                else:
                    return f"{store_name}에서 제공하는 서비스가 등록되지 않았습니다."
            except Store.DoesNotExist:
                return f"{store_name}에 대한 정보를 찾을 수 없습니다."
        else:
            return "가게 이름을 추출하는 데 문제가 발생했습니다. 다시 시도해주세요."

    def get_reservations(self, user):
        stores = Store.objects.filter(ceo=user)
        reservations = Reservation.objects.filter(service__store__in=stores, reservation_time__gte=datetime.now()).order_by('reservation_time')
        if reservations.exists():
            reservation_info = []
            for reservation in reservations:
                reservation_info.append(f"{reservation.reservation_time.strftime('%Y-%m-%d %H:%M')} - {reservation.service.name} ({reservation.customer_name})")
            return f"다가오는 예약 정보입니다:\n" + "\n".join(reservation_info)
        else:
            return "현재 예약된 정보가 없습니다."

    def add_reservation(self, user, query):
        # 예약 추가 로직 구현
        # 쿼리에서 필요한 정보 추출 (날짜, 시간, 서비스, 고객 이름 등)
        # Reservation 객체 생성 및 저장
        return "예약이 추가되었습니다. (구체적인 구현 필요)"

    def get_inventory_info(self, user):
        stores = Store.objects.filter(ceo=user)
        low_stock_items = InventoryItem.objects.filter(store__in=stores, stock__lt=10)
        if low_stock_items.exists():
            items_info = []
            for item in low_stock_items:
                items_info.append(f"{item.name}: {item.stock}개 (안전재고: {item.safety_stock}개)")
            return f"재고가 부족한 항목입니다:\n" + "\n".join(items_info)
        else:
            return "모든 재고가 충분합니다."

    def get_staff_info(self, user):
        stores = Store.objects.filter(ceo=user)
        staff = StoreStaff.objects.filter(store__in=stores)
        if staff.exists():
            staff_info = []
            for employee in staff:
                staff_info.append(f"{employee.user.username} - {employee.role}")
            return f"직원 정보입니다:\n" + "\n".join(staff_info)
        else:
            return "등록된 직원 정보가 없습니다."

    def get_ai_response(self, user, query):
        user_stores = Store.objects.filter(ceo=user)
        store_info = ", ".join([store.name for store in user_stores])
        context = f"사용자의 가게 목록: {store_info}"
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": query}
            ],
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].message['content']
