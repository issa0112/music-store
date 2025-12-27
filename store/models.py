from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType 
import magic
from django.core.exceptions import ValidationError
import mimetypes
from django.contrib.contenttypes.fields import GenericForeignKey
from store.storage_backends import MediaStorage, PublicMediaStorage
from mutagen import File as MutagenFile
from datetime import timedelta 
from django.templatetags.static import static
from django.utils import timezone


class MusicCategory(models.Model):
    name = models.CharField(max_length=100)
    cover_image = models.ImageField(storage=PublicMediaStorage(), upload_to='images/music_category_covers/', blank=True, null=True)

    def __str__(self):
        return self.name

class VideoCategory(models.Model):
    name = models.CharField(max_length=100)
    cover_image = models.ImageField(storage=PublicMediaStorage(), upload_to='images/video_category_covers/', blank=True, null=True)

    def __str__(self):
        return self.name

class Artist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, db_index=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(
        storage=PublicMediaStorage(),   # ✅ B2 public
        upload_to='images/artists/',
        blank=True, null=True
    )
    is_popular = models.BooleanField(default=False, db_index=True)


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
    artist = models.ForeignKey(
        "Artist",
        on_delete=models.CASCADE,
        related_name="albums"
    )
    release_date = models.DateField()
    Music_Category = models.ForeignKey(
        "MusicCategory",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    is_popular = models.BooleanField(default=False, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=9.99)

    # ✅ Cover image → bucket public
    cover_image = models.ImageField(
        storage=PublicMediaStorage(),
        upload_to="images/albums/",
        blank=True,
        null=True
    )

    # ✅ Fichier audio/vidéo → bucket privé (signed URLs)
    fichier = models.FileField(
        storage=MediaStorage(),
        upload_to="media/albums/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.title

    # ✅ Helper pour éviter ValueError si cover_image est vide
    def cover_url(self):
        if self.cover_image:
            return self.cover_image.url
        return static("img/trackdefault.png")

    # ✅ Helper pour générer une URL signée si fichier existe
    def fichier_url(self):
        if self.fichier:
            return self.fichier.storage.url(self.fichier.name)
        return None


from django.core.validators import FileExtensionValidator

def validate_audio_file(value):
    mime = magic.from_buffer(value.read(2048), mime=True)
    value.seek(0)

    # ✅ Vérifie MIME OU extension
    if not (mime.startswith("audio") or value.name.lower().endswith((".mp3",".aac",".wav",".ogg",".flac",".m4a"))):
        raise ValidationError("Seuls les fichiers audio sont autorisés.")


class Track(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    album = models.ForeignKey('Album', on_delete=models.CASCADE, related_name='tracks', null=True, blank=True)
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE, null=True, blank=True, related_name='tracks')
    Music_Category = models.ForeignKey('MusicCategory', on_delete=models.CASCADE, null=True, blank=True)
    
    file = models.FileField(
        storage=MediaStorage(),       # ✅ B2
        upload_to='media/tracks/',
        validators=[validate_audio_file]
    )
    cover_image = models.ImageField(
        storage=PublicMediaStorage(),   # ✅ B2 public
        upload_to='images/tracks/',
        blank=True, null=True
    )

    theme_color = models.CharField(max_length=7, null=True, blank=True)
    duration = models.DurationField(editable=False, null=True, blank=True)  # ✅ auto, non modifiable
    play_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)

    liked_by = models.ManyToManyField(User, blank=True, related_name='liked_tracks')

    def save(self, *args, **kwargs):
        # ✅ Calcul automatique de la durée
        if self.file:
            try:
                audio = MutagenFile(self.file)
                if audio and audio.info:
                    self.duration = timedelta(seconds=int(audio.info.length))
            except Exception as e:
                print(f"⚠️ Impossible de lire la durée du fichier {self.file}: {e}")
        super().save(*args, **kwargs)

    def get_duration_display(self):
        """Affiche la durée formatée mm:ss"""
        if not self.duration:
            return "0:00"
        total_seconds = int(self.duration.total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes}:{seconds:02d}"

    def __str__(self):
        return self.title
    
    def cover_url(self):
        if self.cover_image:
            return self.cover_image.url
        return static("img/trackdefault.png")

    def file_url(self):
        if self.file:
            return self.file.storage.url(self.file.name)
        return None


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


def validate_video_file(value):
    mime = magic.from_buffer(value.read(2048), mime=True)
    value.seek(0)

    allowed_extensions = (".mp4", ".mkv", ".webm", ".mov", ".avi")

    if not (
        mime.startswith("video") 
        or mime in ["application/octet-stream", "binary/octet-stream"]
        or value.name.lower().endswith(allowed_extensions)
    ):
        raise ValidationError("Seuls les fichiers vidéo sont autorisés.")



class Video(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True, blank=True, related_name='videos')
    Video_Category = models.ForeignKey(VideoCategory, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField(blank=True, db_index=True)
    play_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    file =models.FileField(
        storage=MediaStorage(),       # ✅ B2
        upload_to='media/videos/',
        validators=[validate_video_file]
    )
    thumbnail =  models.ImageField(
        storage=PublicMediaStorage(),   # ✅ B2 public
        upload_to='images/videos/',
        blank=True, null=True
    )

    is_popular = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return self.title

    def cover_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        return static("img/trackdefault.png")

    def file_url(self):
        if self.file:
            return self.file.storage.url(self.file.name)
        return None

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
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    etat_paiement = models.CharField(
        max_length=20,
        default="non_payé"
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commande {self.id} - {self.client.username} - {self.etat_paiement}"

    @property
    def total_calculé(self):
        """Calcule automatiquement le total à partir des CommandeAlbum liés"""
        return sum(album.sous_total for album in self.albums.all())

    def save(self, *args, **kwargs):
        # ✅ Met à jour le champ total avant sauvegarde
        self.total = self.total_calculé
        super().save(*args, **kwargs)



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



# store/models.py

class MediaFile(models.Model):
    AUDIO = "audio"
    VIDEO = "video"

    MEDIA_TYPES = [
        (AUDIO, "Audio"),
        (VIDEO, "Video"),
    ]

    STATUS_PENDING = "pending"
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"

    CONVERSION_STATUS = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="uploads/originals/")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    created_at = models.DateTimeField(default=timezone.now)

    # Champs pour stocker les versions converties
    opus_file = models.FileField(upload_to="uploads/converted/audio/", blank=True, null=True)
    aac_file = models.FileField(upload_to="uploads/converted/audio/", blank=True, null=True)
    mp4_file = models.FileField(upload_to="uploads/converted/video/", blank=True, null=True)
    webm_file = models.FileField(upload_to="uploads/converted/video/", blank=True, null=True)

    # Thumbnails (pour vidéo)
    thumbnail = models.ImageField(upload_to="uploads/thumbnails/", blank=True, null=True)

    # Statut de conversion
    conversion_status = models.CharField(
        max_length=20,
        choices=CONVERSION_STATUS,
        default=STATUS_PENDING,
        db_index=True
    )

    def __str__(self):
        return f"{self.title} ({self.media_type}) - {self.conversion_status}"
