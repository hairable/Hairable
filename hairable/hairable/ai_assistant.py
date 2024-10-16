import openai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .config import OPENAI_API_KEY
from service.models import Reservation  # 예약 모델
from stores.models import Store  # 가게 모델
from service.models import Service  # 서비스 모델
import re
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


class AIAssistantView(APIView):
    authentication_classes = [JWTAuthentication]  # JWT 인증 사용
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def post(self, request):
        user = request.user  # 로그인한 사용자 정보
        user_query = request.data.get("query")
        if not user_query:
            return Response({"error": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)

        response_content = ""

        # 특정 가게의 서비스 조회 (사용자와 관련된 가게만 조회 가능)
        if "서비스" in user_query and "제공" in user_query:
            # 정규 표현식을 사용해 가게 이름 추출
            match = re.search(r'(.+?)는 어떤 서비스를 제공', user_query)
            if match:
                store_name = match.group(1).strip()
                try:
                    # 로그인한 사용자와 관련된 가게만 조회
                    store = Store.objects.get(name=store_name, ceo=user)
                    services = Service.objects.filter(store=store)
                    if services.exists():
                        service_names = [service.name for service in services]
                        response_content = f"{store_name}에서 제공하는 서비스는 다음과 같습니다: {', '.join(service_names)}."
                    else:
                        response_content = f"{store_name}에서 제공하는 서비스가 등록되지 않았습니다."
                except Store.DoesNotExist:
                    response_content = f"{store_name}에 대한 정보를 찾을 수 없습니다."
            else:
                response_content = "가게 이름을 추출하는 데 문제가 발생했습니다. 다시 시도해주세요."
        else:
            try:
                # AI 응답 생성 (로그인한 사용자와 관련된 정보를 포함하여 응답 생성)
                user_stores = Store.objects.filter(ceo=user)
                store_info = ", ".join([store.name for store in user_stores])
                context = f"사용자의 가게 목록: {store_info}"
                
                # OpenAI API 호출 (예외 처리 추가)
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": context},
                        {"role": "user", "content": user_query}
                    ],
                    max_tokens=150,
                    temperature=0.7,
                )
                response_content = response.choices[0].message['content']
            except Exception as e:
                # OpenAI API 호출 중 발생한 예외 처리
                return Response({"error": "AI 요청 처리 중 오류가 발생했습니다.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"response": response_content}, status=status.HTTP_200_OK)
