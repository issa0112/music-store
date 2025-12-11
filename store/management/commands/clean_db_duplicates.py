from django.core.management.base import BaseCommand
from store.models import Album, Video, Artist, MusicCategory, VideoCategory, Track

class Command(BaseCommand):
    help = 'Remove duplicate database entries for models.'

    def handle(self, *args, **options):
        # Clean Artist duplicates (by name)
        artists = Artist.objects.all()
        seen_names = set()
        for artist in artists:
            if artist.name in seen_names:
                artist.delete()
                self.stdout.write(f'Deleted duplicate Artist: {artist.name}')
            else:
                seen_names.add(artist.name)

        # Clean MusicCategory duplicates (by name)
        music_cats = MusicCategory.objects.all()
        seen_names = set()
        for cat in music_cats:
            if cat.name in seen_names:
                cat.delete()
                self.stdout.write(f'Deleted duplicate MusicCategory: {cat.name}')
            else:
                seen_names.add(cat.name)

        # Clean VideoCategory duplicates (by name)
        video_cats = VideoCategory.objects.all()
        seen_names = set()
        for cat in video_cats:
            if cat.name in seen_names:
                cat.delete()
                self.stdout.write(f'Deleted duplicate VideoCategory: {cat.name}')
            else:
                seen_names.add(cat.name)

        # Clean Album duplicates (by title and artist)
        albums = Album.objects.all()
        seen = set()
        for album in albums:
            key = (album.title, album.artist_id)
            if key in seen:
                album.delete()
                self.stdout.write(f'Deleted duplicate Album: {album.title}')
            else:
                seen.add(key)

        # Clean Track duplicates (by title and artist)
        tracks = Track.objects.all()
        seen = set()
        for track in tracks:
            key = (track.title, track.artist_id)
            if key in seen:
                track.delete()
                self.stdout.write(f'Deleted duplicate Track: {track.title}')
            else:
                seen.add(key)

        # Clean Video duplicates (by title)
        videos = Video.objects.all()
        seen_titles = set()
        for video in videos:
            if video.title in seen_titles:
                video.delete()
                self.stdout.write(f'Deleted duplicate Video: {video.title}')
            else:
                seen_titles.add(video.title)

        self.stdout.write('Database duplicates cleaned.')
