from django.urls import path
from . import views
urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('find-username/', views.FindUsernameAPIView.as_view(), name='find-username'),
    path('reset-password/', views.ResetPasswordAPIView.as_view(), name='reset-password'),
]

