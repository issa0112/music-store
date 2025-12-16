from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from store.storage_backends import MediaStorage

class MusicCategory(models.Model):
    name = models.CharField(max_length=100)
    cover_image = models.ImageField(upload_to='music_category_covers/', blank=True, null=True)

    def __str__(self):
        return self.name

class VideoCategory(models.Model):  # ✅ Conservez cette définition
    name = models.CharField(max_length=100)
    cover_image = models.ImageField(upload_to='video_category_covers/', blank=True, null=True)
    def __str__(self):
        return self.name

class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, db_index=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='artists/', blank=True, null=True)
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.name
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follows')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'artist')


class Album(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')
    release_date = models.DateField()
    Music_Category = models.ForeignKey(MusicCategory, on_delete=models.CASCADE, null=True, blank=True)
    is_popular = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=9.99)
    cover_image = models.ImageField(upload_to='album_covers/', blank=True, null=True)
    fichier = models.FileField(upload_to='albums/', blank=True, null=True)


    def __str__(self):
        return self.title



class Track(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='tracks', null=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True, related_name='tracks')
    Music_Category = models.ForeignKey(MusicCategory, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='tracks/')
    cover_image = models.ImageField(upload_to='track_covers/', blank=True, null=True)

    theme_color = models.CharField(max_length=7, null=True, blank=True)
    duration = models.DurationField()
    play_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)

    liked_by = models.ManyToManyField(User, blank=True, related_name='liked_tracks')

    def __str__(self):
        return self.title


class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    name = models.CharField(max_length=100, default="Ma Playlist")
    tracks = models.ManyToManyField(Track, blank=True, related_name='in_playlists')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"





class UserAction(models.Model):
    ACTION_CHOICES = [
        ('like', 'Like'),
        ('follow', 'Follow'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=10, choices=ACTION_CHOICES)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'action_type', 'content_type', 'object_id')


class Video(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True, related_name='videos')
    Video_Category = models.ForeignKey(VideoCategory, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True, db_index=True)
    play_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='video_thumbnails/', blank=True, null=True)

    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, null=True, blank=True, on_delete=models.SET_NULL)
    video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.track or self.video}'

class ArtistOrSuperuserRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser or Artist.objects.filter(user=request.user).exists():
            return super().dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied


class Commande(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    etat_paiement = models.CharField(
        max_length=20,
        default="non_payé"  # valeurs possibles: non_payé, en_attente, payé, échoué
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande {self.id} - {self.client.username}"


class CommandeAlbum(models.Model):
    commande = models.ForeignKey(Commande, related_name="albums", on_delete=models.CASCADE)
    album = models.ForeignKey('Album', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)  # copie du titre de l'album
    price = models.DecimalField(max_digits=6, decimal_places=2)  # copie du prix
    quantite = models.PositiveIntegerField(default=1)
    sous_total = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def save(self, *args, **kwargs):
        self.sous_total = self.price * self.quantite
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} x {self.quantite}"