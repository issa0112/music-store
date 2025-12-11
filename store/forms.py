from django import forms
from .models import Track, Video, Artist
from Utilisateurs.models import Profile

class TrackUploadForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ['title', 'album', 'file', 'duration']

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'file', 'description']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'location', 'website']

class ArtistProfileForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = ['name', 'bio', 'image']
