from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Recipe(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField()
    instructions = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # NEW: Likes field
    likes = models.ManyToManyField(User, related_name="liked_recipes", blank=True)

    # Saved recipes field
    saved_by = models.ManyToManyField(User, related_name="saved_recipes", blank=True)

    def total_likes(self):
        """Return the total number of likes for this recipe."""
        return self.likes.count()

    def __str__(self):
        return self.title


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.recipe.title}"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="ratings")
    value = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')  # Each user can rate once


@property
def average_rating(self):
    agg = self.ratings.aggregate(avg=models.Avg('value'))
    return agg['avg'] or 0

def user_rating_for(self, user):
    rating = self.ratings.filter(user=user).first()
    return rating.value if rating else 0