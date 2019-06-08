from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logged/', views.Logged.as_view(), name='logged'),
    path('logout/', auth_views.LogoutView.as_view(template_name='accounts/thanks.html'), name='logout'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('change_password/', auth_views.PasswordChangeView.as_view(template_name='accounts/change_password.html'), name='change_password'),

]
