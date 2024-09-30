from django.urls import path
from . import views
urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('find-username/', views.FindUsernameAPIView.as_view(), name='find-username'),
    path('reset-password/', views.ResetPasswordAPIView.as_view(), name='reset-password'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('userlist/', views.UserListCreateView.as_view(), name='userlist'),
    path('signup/', views.UserListCreateView.as_view(), name='signup'),
    path('profile/', views.ProfileAPIView.as_view(), name='profile'),
    path('profile/<int:pk>', views.UserProfileAPIView.as_view(), name='user-profile'),
]

