from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages

from .models import Recipe, Rating, Comment
from .forms import RecipeForm


# List view with search functionality
class RecipeListView(ListView):
    model = Recipe
    template_name = "recipes/recipe_list.html"
    context_object_name = "recipes"
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(description__icontains=query))
        return queryset.annotate(average_rating=Avg('ratings__value'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Top 3 liked recipes
        context["favorites"] = Recipe.objects.annotate(
            num_likes=Count('likes'),
            average_rating=Avg('ratings__value')
        ).order_by('-num_likes')[:3]

        context["search_query"] = self.request.GET.get("q", "")
        return context


# AJAX search for live search
def ajax_search_recipes(request):
    query = request.GET.get('q', '')
    recipes = Recipe.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))\
        .annotate(average_rating=Avg('ratings__value')).order_by('-created_at')
    html = render_to_string('recipes/partials/recipe_cards.html', {'recipes': recipes, 'user': request.user})
    return JsonResponse({'html': html})


# Detail view
class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipes/recipe_detail.html"
    context_object_name = "recipe"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.object
        user = self.request.user

        # Current user's rating
        if user.is_authenticated:
            rating = recipe.ratings.filter(user=user).first()
            context['user_rating'] = rating.value if rating else 0
        else:
            context['user_rating'] = 0

        # Average rating
        context['average_rating'] = recipe.ratings.aggregate(avg=Avg('value'))['avg'] or 0
        return context


# Create view
class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"
    success_url = reverse_lazy("recipe_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


# Like / Unlike
@login_required
def toggle_like(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user
    if user in recipe.likes.all():
        recipe.likes.remove(user)
    else:
        recipe.likes.add(user)
    return redirect(request.META.get('HTTP_REFERER', 'recipe_list'))


# Save / Unsave (reuse toggle)
@login_required
def toggle_save(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user
    if user in recipe.saved_by.all():
        recipe.saved_by.remove(user)
    else:
        recipe.saved_by.add(user)
    return redirect(request.META.get('HTTP_REFERER', 'recipe_list'))


# Add comment
@login_required
def add_comment(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Comment.objects.create(recipe=recipe, author=request.user, content=content)
            messages.success(request, "Comment added successfully!")
    return redirect('recipe_detail', pk=pk)


# Delete comment
@login_required
def delete_comment(request, pk, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    comment.delete()
    messages.success(request, "Comment deleted!")
    return redirect('recipe_detail', pk=pk)


# Rate recipe (5-star)
@login_required
def recipe_rate(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == "POST":
        value = int(request.POST.get("rating", 0))
        if 1 <= value <= 5:
            Rating.objects.update_or_create(
                user=request.user,
                recipe=recipe,
                defaults={'value': value}
            )
    return redirect('recipe_detail', pk=pk)
