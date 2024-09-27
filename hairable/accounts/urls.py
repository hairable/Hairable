from django.urls import path
from . import views
urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('find-username/', views.FindUsernameAPIView.as_view(), name='find-username'),
    path('reset-password/', views.ResetPasswordAPIView.as_view(), name='reset-password'),
    path('acc_edit/<str:username>/', views.AccEditAPIView.as_view(), name='acc_edit'),
    path('profile_edit/<str:username>/', views.ProfileEditAPIView.as_view(), name='profile_edit'),
]

