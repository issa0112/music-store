import os
from django.core.files import File
from django.core.management.base import BaseCommand
from store.models import Artist, Album, Track, Video, MusicCategory, VideoCategory
from storages.backends.s3boto3 import S3Boto3Storage
from datetime import timedelta

# Initialise le storage B2
s3_storage = S3Boto3Storage()

class Command(BaseCommand):
    help = "Upload media files sur Backblaze B2 et mettre à jour les modèles"

    def add_arguments(self, parser):
        parser.add_argument(
            'media_root',
            nargs='?',
            default='media',
            type=str,
            help='Chemin vers le dossier local contenant les fichiers media'
        )

    def handle(self, *args, **options):
        media_root = options['media_root']
        self.stdout.write(f"Migration des fichiers depuis : {media_root}")
        migrate_all(media_root)
        self.stdout.write("Migration terminée !")


def upload_file(obj, field_name, local_path, media_root):
    """Upload un fichier sur B2 et met à jour le champ du modèle"""
    if not os.path.exists(local_path):
        print(f"Fichier introuvable : {local_path}")
        return

    field = getattr(obj, field_name)
    relative_path = os.path.relpath(local_path, media_root)  # garde la structure
    # Evite de ré-upload si déjà présent
    if field and field.name and s3_storage.exists(relative_path):
        print(f"{field_name} déjà présent : {relative_path}")
        return

    with open(local_path, 'rb') as f:
        saved_name = s3_storage.save(relative_path, File(f))
        field.name = saved_name
        obj.save()
        print(f"Upload réussi : {local_path} → {saved_name}")


def convert_duration(duration_str):
    """Convertit 'mm:ss' ou 'hh:mm:ss' en timedelta"""
    parts = [int(p) for p in duration_str.split(':')]
    if len(parts) == 2:
        return timedelta(minutes=parts[0], seconds=parts[1])
    elif len(parts) == 3:
        return timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])
    return timedelta()


def migrate_all(media_root):
    """Parcours tous les objets et upload leurs fichiers"""
    # Artistes
    for artist in Artist.objects.all():
        if artist.image:
            path = os.path.join(media_root, 'artists', os.path.basename(artist.image.name))
            upload_file(artist, 'image', path, media_root)

    # Albums
    for album in Album.objects.all():
        if album.cover_image:
            path = os.path.join(media_root, 'album_covers', os.path.basename(album.cover_image.name))
            upload_file(album, 'cover_image', path, media_root)
        if album.fichier:
            path = os.path.join(media_root, 'albums', os.path.basename(album.fichier.name))
            upload_file(album, 'fichier', path, media_root)

    # Tracks
    for track in Track.objects.all():
        if track.file:
            path = os.path.join(media_root, 'tracks', os.path.basename(track.file.name))
            upload_file(track, 'file', path, media_root)
        if track.cover_image:
            path = os.path.join(media_root, 'track_covers', os.path.basename(track.cover_image.name))
            upload_file(track, 'cover_image', path, media_root)
        if track.duration and isinstance(track.duration, str):
            track.duration = convert_duration(track.duration)
            track.save()

    # Videos
    for video in Video.objects.all():
        if video.file:
            path = os.path.join(media_root, 'videos', os.path.basename(video.file.name))
            upload_file(video, 'file', path, media_root)
        if video.thumbnail:
            path = os.path.join(media_root, 'video_thumbnails', os.path.basename(video.thumbnail.name))
            upload_file(video, 'thumbnail', path, media_root)

    # MusicCategory
    for cat in MusicCategory.objects.all():
        if cat.cover_image:
            path = os.path.join(media_root, 'music_category_covers', os.path.basename(cat.cover_image.name))
            upload_file(cat, 'cover_image', path, media_root)

    # VideoCategory
    for cat in VideoCategory.objects.all():
        if cat.cover_image:
            path = os.path.join(media_root, 'video_category_covers', os.path.basename(cat.cover_image.name))
            upload_file(cat, 'cover_image', path, media_root)

