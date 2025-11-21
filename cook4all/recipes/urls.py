from django.urls import path
from .views import RecipeListView, RecipeDetailView, RecipeCreateView

urlpatterns = [
    path("", RecipeListView.as_view(), name="recipe_list"),
    path("new/", RecipeCreateView.as_view(), name="recipe_create"),
    path("<int:pk>/", RecipeDetailView.as_view(), name="recipe_detail"),
]