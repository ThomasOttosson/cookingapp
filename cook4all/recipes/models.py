from django.db import models
from django.contrib.auth.models import User


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField()
    instructions = models.TextField()
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # NEW: Likes field
    likes = models.ManyToManyField(User, related_name="liked_recipes", blank=True)

    def total_likes(self):
        """Return the total number of likes for this recipe."""
        return self.likes.count()

    def __str__(self):
        return self.title
