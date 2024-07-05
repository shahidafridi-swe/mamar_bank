from django.urls import path

from . import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('password_change/', views.changePassword, name='password_change'),
    path('profile/', views.UserBankAccountUpdateView.as_view(), name='profile' ),
]
