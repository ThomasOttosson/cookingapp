from django.urls import path
from . import views

urlpatterns = [
    path('saved/', views.SavedRecipesView.as_view(), name='saved_recipes'),
    path('account/', views.AccountInfoView.as_view(), name='account_info'),
    path('toggle-save/<int:pk>/', views.toggle_save, name='toggle_save'),
]
