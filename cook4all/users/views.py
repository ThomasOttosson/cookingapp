from django.shortcuts import render, get_object_or_404, redirect

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from recipes.models import Recipe  # Import Recipe model

from django.contrib.auth.decorators import login_required


@login_required
def toggle_save(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    user = request.user
    if user in recipe.saved_by.all():
        recipe.saved_by.remove(user)
    else:
        recipe.saved_by.add(user)
    return redirect(request.META.get('HTTP_REFERER', 'recipe_list'))


class SavedRecipesView(LoginRequiredMixin, TemplateView):
    template_name = 'users/saved_recipes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch saved recipes for the logged-in user
        context['saved_recipes'] = self.request.user.saved_recipes.all()
        return context


class AccountInfoView(LoginRequiredMixin, TemplateView):
    template_name = 'users/account_info.html'
