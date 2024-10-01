from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse


# email 전송
def send_verification_email(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    
    # 인증 링크 생성
    verification_link = request.build_absolute_uri(
        reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
    )
    
    # 이메일 보내기
    send_mail(
        '이메일 인증을 완료해주세요.',
        f'아래 링크를 클릭하여 이메일 인증을 완료하세요: {verification_link}',
        'noreply@mydomain.com',
        [user.email],
        fail_silently=False,
    )