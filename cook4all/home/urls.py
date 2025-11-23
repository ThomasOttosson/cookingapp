from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path("signout/", views.logout_confirm, name="logout_confirm"),
    path("logout/", views.logout_view, name="logout"),
    path('register/', views.register, name='register'),
    path('recipe/<int:pk>/like/', views.toggle_like, name='toggle_like'),
]
