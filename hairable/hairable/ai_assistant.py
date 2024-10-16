import openai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .config import OPENAI_API_KEY
from service.models import Reservation, Service
from stores.models import Store, StoreStaff
from inventory.models import InventoryItem  # 추가된 재고 모델 import
import re
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

class AIAssistantView(APIView):
    authentication_classes = [JWTAuthentication]  # JWT 인증 사용
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def post(self, request):
        openai.api_key = OPENAI_API_KEY
        user = request.user  # 로그인한 사용자 정보
        user_query = request.data.get("query")
        if not user_query:
            return Response({"error": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)

        response_content = ""

        try:
            # 사용자와 관련된 모든 매장의 정보를 조회
            user_stores = Store.objects.filter(ceo=user)
            store_info = []

            for store in user_stores:
                # 매장 관련 서비스 정보
                services = Service.objects.filter(store=store)
                services_data = [service.name for service in services]

                # 매장 관련 직원 정보
                store_staff = StoreStaff.objects.filter(store=store)
                staff_data = [
                    {
                        "name": staff.user.username,
                        "role": staff.role,
                        "available_services": [service.name for service in staff.available_services.all()],
                    }
                    for staff in store_staff
                ]

                # 매장 관련 재고 정보
                # InventoryItem에 Store와 직접 연결된 필드가 없을 경우 수정 필요
                inventory_data = InventoryItem.objects.filter(serviceinventory__service__store=store).distinct()
                inventory_details = [
                    {
                        "name": inventory.name,
                        "stock": inventory.stock,
                        "category": inventory.category.name
                    }
                    for inventory in inventory_data
                ]

                # 매장 정보 구성
                store_details = {
                    "name": store.name,
                    "services": services_data,
                    "staff": staff_data,
                    "inventory": inventory_details
                }
                store_info.append(store_details)

            # 컨텍스트 생성
            context = f"사용자의 가게 정보: {store_info}"

            # OpenAI API 호출 (유연한 응답 생성)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": context},
                    {"role": "user", "content": user_query}
                ],
                max_tokens=200,
                temperature=0.7,
            )
            response_content = response.choices[0].message['content']

        except Exception as e:
            # OpenAI API 호출 중 발생한 예외 처리
            return Response({"error": "AI 요청 처리 중 오류가 발생했습니다.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"response": response_content}, status=status.HTTP_200_OK)
