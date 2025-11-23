from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages

from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from recipes.models import Recipe, Rating
from django.db.models import Count, Avg


@login_required
def logout_confirm(request):
    return render(request, "logout_confirm.html")


@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")


def home(request):
    # ⭐ Top 3 Most Liked Recipes
    top_recipes = (
        Recipe.objects
        .annotate(total_likes_count=Count("likes"))  # "likes" = ManyToManyField
        .order_by("-total_likes_count")[:3]
    )

    # ⭐ Top 3 Rated Recipes
    top_rated = (
        Recipe.objects
        .annotate(avg_rating=Avg("ratings__value"))  # average rating from Rating model
        .order_by("-avg_rating")[:3]
    )

    return render(request, 'home/home.html', {
        "top_recipes": top_recipes,
        "top_rated": top_rated
    })


# registration view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def toggle_like(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    if request.user in recipe.likes.all():
        recipe.likes.remove(request.user)
    else:
        recipe.likes.add(request.user)

    return redirect(request.META.get("HTTP_REFERER", "recipe_list"))


@login_required
def toggle_save(request, pk):
    """Save or unsave a recipe for the logged-in user."""
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user
    if user in recipe.saved_by.all():
        recipe.saved_by.remove(user)
    else:
        recipe.saved_by.add(user)
    return redirect(request.META.get("HTTP_REFERER", "recipe_list"))
