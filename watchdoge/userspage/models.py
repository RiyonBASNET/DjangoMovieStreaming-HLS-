from django.db import models
from streaming.models import Movie
from django.contrib.auth.models import User
from django.conf import settings


# Create your models here.

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')  # prevents duplicates

    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"

class WatchHistory(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-watched_at']
    
    def __str__(self):
        return f"{self.user.username} watched {self.movie.title}"

class Watchlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')  # prevents duplicates
