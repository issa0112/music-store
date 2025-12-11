from django.db import models

# models.py
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='default.jpg')
    bio = models.TextField(blank=True, help_text="Courte biographie")
    location = models.CharField(max_length=100, blank=True, help_text="Lieu de résidence")
    website = models.URLField(blank=True, help_text="Site web personnel")

    def __str__(self):
        return self.user.username
