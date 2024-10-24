from django.urls import path
from . import views

app_name = 'accounts'  # 네임스페이스 설정

urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('find-username/', views.FindUsernameAPIView.as_view(), name='find-username'),
    path('password-change/', views.ChangePasswordAPIView.as_view(), name='password_change'),
    path('password-reset/', views.ResetPasswordAPIView.as_view(), name='password_reset'),
    path('password-reset/confirm/<uidb64>/<token>/', views.ResetPasswordAPIView.as_view(), name='password_reset_confirm'),
    path('userlist/', views.UserListCreateView.as_view(), name='userlist'),
    path('userUD/', views.UserUpdateDeleteAPIView.as_view(), name='user-update-delete'),
    path('signup/', views.UserListCreateView.as_view(), name='signup'),
    path('profile/', views.ProfileAPIView.as_view(), name='profile'),
    path('profile/<int:pk>/', views.UserProfileAPIView.as_view(), name='user-profile'),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
]
