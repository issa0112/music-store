from django.test import TestCase, Client
from django.urls import reverse
from .models import Track, Artist, Album, MusicCategory
from datetime import timedelta

class PlayTrackTest(TestCase):
    def setUp(self):
        # Create required related objects
        self.artist = Artist.objects.create(name="Test Artist")
        self.category = MusicCategory.objects.create(name="Test Category")
        self.album = Album.objects.create(
            title="Test Album",
            artist=self.artist,
            release_date="2023-01-01",
            Music_Category=self.category
        )
        # Create a test track
        self.track = Track.objects.create(
            title="Test Track",
            album=self.album,
            artist=self.artist,
            file="test.mp3",
            Music_Category=self.category,
            duration=timedelta(minutes=3),
            play_count=0
        )

    def test_play_count_increment(self):
        """Test that play_track increments the play_count."""
        initial_count = self.track.play_count
        client = Client()
        response = client.get(reverse('play_track', args=[self.track.id]))
        self.track.refresh_from_db()
        self.assertEqual(self.track.play_count, initial_count + 1)
        self.assertEqual(response.status_code, 200)
