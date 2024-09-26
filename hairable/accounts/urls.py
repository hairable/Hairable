from django.urls import path
from . import views

urlpatterns = [
    path("", views.UserCreateView.as_view()),
    path('members/', views.UserList.as_view()),
    path('members/<int:pk>/', views.UserDetail.as_view()),
    path("profile<str:username>/", views.UserProfileView.as_view()),
]