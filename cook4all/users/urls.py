from django.urls import path
from . import views
from .views import edit_profile

urlpatterns = [
    path('saved/', views.SavedRecipesView.as_view(), name='saved_recipes'),
    path('account/', views.AccountInfoView.as_view(), name='account_info'),
    path('toggle-save/<int:pk>/', views.toggle_save, name='toggle_save'),
    path("edit/", edit_profile, name="edit_profile"),
]
