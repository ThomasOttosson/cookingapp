from django.urls import path
from .views import RecipeListView, RecipeDetailView, RecipeCreateView, toggle_like
from .views import ajax_search_recipes
from . import views


urlpatterns = [
    path("", RecipeListView.as_view(), name="recipe_list"),
    path("new/", RecipeCreateView.as_view(), name="recipe_create"),
    path("<int:pk>/", RecipeDetailView.as_view(), name="recipe_detail"),
    path("<int:pk>/like/", toggle_like, name="recipe_like"),  # <-- Like/unlike view
    path('ajax/search/', ajax_search_recipes, name='ajax_search_recipes'),
    path('recipe/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('recipe/<int:pk>/comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]
