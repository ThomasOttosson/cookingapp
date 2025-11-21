from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView, DetailView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Recipe

from .forms import RecipeForm
from django.contrib.auth.decorators import login_required
from django.db import models

from django.db.models import Q  # NEW: Needed for search filtering
from django.http import JsonResponse  # NEW: For AJAX search
from django.template.loader import render_to_string  # NEW: Render partial template for AJAX

from django.contrib import messages
from .models import Comment

# List view with search functionality
class RecipeListView(ListView):
    model = Recipe
    template_name = "recipes/recipe_list.html"
    context_object_name = "recipes"
    ordering = ["-created_at"]

    # NEW: Filter queryset based on search query (for normal GET requests)
    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")  # Get search query from GET params
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Favorites based on number of likes
        context["favorites"] = Recipe.objects.annotate(
            num_likes=models.Count('likes')
        ).order_by('-num_likes')[:3]

        # NEW: Pass search query back to template to pre-fill input
        context["search_query"] = self.request.GET.get("q", "")

        return context


# NEW: AJAX search view for live instant search
def ajax_search_recipes(request):
    query = request.GET.get('q', '')
    recipes = Recipe.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ).order_by('-created_at')

    # Render only the recipes grid (partial template)
    html = render_to_string('recipes/partials/recipe_cards.html', {'recipes': recipes, 'user': request.user})
    return JsonResponse({'html': html})


# Detail view
class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipes/recipe_detail.html"
    context_object_name = "recipe"


# Create view
class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"
    success_url = reverse_lazy("recipe_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# Like / Unlike view
@login_required
def toggle_like(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user
    if user in recipe.likes.all():
        recipe.likes.remove(user)
    else:
        recipe.likes.add(user)
    # redirect back to the page that triggered the like
    return redirect(request.META.get('HTTP_REFERER', 'recipe_list'))


@login_required
def add_comment(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Comment.objects.create(recipe=recipe, author=request.user, content=content)
            messages.success(request, "Comment added successfully!")
    return redirect('recipe_detail', pk=pk)


@login_required
def delete_comment(request, pk, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    comment.delete()
    messages.success(request, "Comment deleted!")
    return redirect('recipe_detail', pk=pk)
