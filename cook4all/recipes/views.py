from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib import messages
from .models import Recipe, Rating, Comment
from .forms import RecipeForm


# ---------------------------------------
# Recipe List View (search + filters + pagination)
# ---------------------------------------
class RecipeListView(ListView):
    model = Recipe
    template_name = "recipes/recipe_list.html"
    context_object_name = "recipes"
    ordering = ["-created_at"]


    # Main queryset
    def get_queryset(self):
        queryset = super().get_queryset()

        # Search
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query)
            )

        # ⭐ FILTER OPTION (toggle)
        filter_option = self.request.GET.get("filter")

        # ---------------------------------------
        # Most Liked filter
        # ---------------------------------------
        if filter_option == "most_liked":
            queryset = (
                queryset.annotate(like_count=Count("likes"))
                .filter(like_count__gt=0)  # only recipes with likes
                .order_by("-like_count")
            )

        # ---------------------------------------
        # Top Rated filter
        # ---------------------------------------
        if filter_option == "top_rated":
            queryset = (
                queryset.annotate(avg_rating=Avg("ratings__value"))
                .filter(avg_rating__gt=0)  # only rated recipes
                .order_by("-avg_rating")
            )

        return queryset


    # Context
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Search query
        context["search_query"] = self.request.GET.get("q", "")

        # Active filter for toggling button UI
        context["filter_option"] = self.request.GET.get("filter", "")

        # Pagination
        recipes = context["recipes"]
        paginator = Paginator(recipes, 6)
        page_obj = paginator.get_page(self.request.GET.get("page"))
        context["recipes"] = page_obj

        # ⭐ Top 3 Liked Recipes
        context["favorites"] = (
            Recipe.objects.annotate(num_likes=Count("likes"))
            .order_by("-num_likes")[:3]
        )

        # ⭐ Top 3 Rated Recipes
        context["top_rated"] = (
            Recipe.objects.annotate(avg_rating=Avg("ratings__value"))
            .order_by("-avg_rating")[:3]
        )

        return context



# ---------------------------------------
# AJAX Search (live search)
# ---------------------------------------
def ajax_search_recipes(request):
    query = request.GET.get('q', '')
    recipes = Recipe.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query)
    ).order_by('-created_at')

    html = render_to_string(
        'recipes/partials/recipe_cards.html',
        {'recipes': recipes, 'user': request.user}
    )

    return JsonResponse({'html': html})


# ---------------------------------------
# Detail View
# ---------------------------------------
class RecipeDetailView(DetailView):
    model = Recipe
    template_name = "recipes/recipe_detail.html"
    context_object_name = "recipe"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        recipe = self.object
        user = self.request.user

        # User rating
        if user.is_authenticated:
            rating = recipe.ratings.filter(user=user).first()
            context['user_rating'] = rating.value if rating else 0
        else:
            context['user_rating'] = 0

        # Average rating
        context['average_rating'] = recipe.average_rating

        return context


# ---------------------------------------
# Create Recipe
# ---------------------------------------
class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = "recipes/recipe_form.html"
    success_url = reverse_lazy("recipe_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)



# ---------------------------------------
# Like / Unlike
# ---------------------------------------
@login_required
def toggle_like(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user

    if user in recipe.likes.all():
        recipe.likes.remove(user)
    else:
        recipe.likes.add(user)

    return redirect(request.META.get('HTTP_REFERER', 'recipe_list'))


# ---------------------------------------
# Save / Unsave
# ---------------------------------------
@login_required
def toggle_save(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user

    if user in recipe.saved_by.all():
        recipe.saved_by.remove(user)
    else:
        recipe.saved_by.add(user)

    return redirect(request.META.get('HTTP_REFERER', 'recipe_list'))



# ---------------------------------------
# Add Comment
# ---------------------------------------
@login_required
def add_comment(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Comment.objects.create(
                recipe=recipe,
                author=request.user,
                content=content
            )
            messages.success(request, "Comment added successfully!")
        return redirect('recipe_detail', pk=pk)



# ---------------------------------------
# Delete Comment
# ---------------------------------------
@login_required
def delete_comment(request, pk, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    comment.delete()
    messages.success(request, "Comment deleted!")
    return redirect('recipe_detail', pk=pk)



# ---------------------------------------
# Edit Comment
# ---------------------------------------
@login_required
def edit_comment(request, pk, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)

    if request.method == "POST":
        new_content = request.POST.get("content")
        if new_content:
            comment.content = new_content
            comment.save()
            messages.success(request, "Comment updated!")
        return redirect('recipe_detail', pk=pk)



# ---------------------------------------
# Rate Recipe
# ---------------------------------------
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
