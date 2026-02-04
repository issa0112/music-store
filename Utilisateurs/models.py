from django.db import models
from django.contrib.auth.models import User
from store.models import Track  # si Track est dans store.models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='default-avatar.png')
    cover = models.ImageField(upload_to='covers/', default='default-cover.jpg')

    liked_tracks = models.ManyToManyField(Track, blank=True, related_name='liked_by_users')
    following = models.ManyToManyField(User, blank=True, related_name='followers')

    def __str__(self):
        return self.user.username
