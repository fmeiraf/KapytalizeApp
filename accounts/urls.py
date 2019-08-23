from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('sua_conta/', views.SuaConta.as_view(), name='sua-conta'),
    path('logged/', views.Logged.as_view(), name='logged'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/thanks.html'), name='logout'),
    path('password_reset/',
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('change_password/', auth_views.PasswordChangeView.as_view(template_name='accounts/change_password.html'), name='change_password'),
]
