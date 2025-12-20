from django.contrib import admin
from .models import *
from django import forms
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db import transaction
from django.template.response import TemplateResponse
from django.urls import reverse

# Enregistrement des modèles dans l'admin
admin.site.register(Album)
admin.site.register(Purchase)
admin.site.register(Artist)
admin.site.register(VideoCategory)
admin.site.register(MusicCategory)
admin.site.register(UserAction)


# Utilisation du décorateur pour Track et Video
@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'album', 'play_count', 'download_count']
    readonly_fields = ('duration',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'play_count', 'download_count']


# Amélioration de l'admin pour Playlist
class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = '__all__'

    def clean(self):
        cleaned = super().clean()
        user = cleaned.get('user')
        name = cleaned.get('name')
        if user and name:
            qs = Playlist.objects.filter(user=user, name__iexact=name)
            # exclure l'instance en cours lors de la modification
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError({'name': 'Vous avez déjà une playlist avec ce nom.'})
        return cleaned


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    form = PlaylistForm
    list_display = ['user', 'name', 'created_at']
    search_fields = ['name', 'user__username']
    list_filter = ['created_at']
    actions = ['merge_playlists']

    def merge_playlists(self, request, queryset):
        """Admin action to merge selected playlists per user.

        This action first shows a confirmation page listing playlists grouped
        by user. When the admin confirms, it merges playlists per user
        (keeps the earliest playlist as target), moves tracks and deletes others.
        """
        # If the confirmation form was submitted, perform the merge
        if request.method == 'POST' and request.POST.get('confirm') == 'yes':
            selected_ids = request.POST.getlist('selected')
            if len(selected_ids) < 2:
                self.message_user(request, "Sélectionnez au moins deux playlists à fusionner.", level=messages.WARNING)
                return None

            qs = Playlist.objects.filter(pk__in=selected_ids).select_related('user')
            # Group selected playlists by user
            playlists_by_user = {}
            for pl in qs:
                playlists_by_user.setdefault(pl.user_id, []).append(pl)

            total_deleted = 0
            with transaction.atomic():
                for user_id, pls in playlists_by_user.items():
                    if len(pls) < 2:
                        continue
                    pls_sorted = sorted(pls, key=lambda p: p.id)
                    target = pls_sorted[0]
                    others = pls_sorted[1:]
                    for other in others:
                        for t in other.tracks.all():
                            target.tracks.add(t)
                        other.delete()
                        total_deleted += 1

            self.message_user(request, f"Fusion terminée — {total_deleted} playlists supprimées et leurs pistes ajoutées.", level=messages.INFO)
            # Redirect back to the changelist
            return None

        # Otherwise render confirmation page
        if queryset.count() < 2:
            self.message_user(request, "Sélectionnez au moins deux playlists à fusionner.", level=messages.WARNING)
            return

        # Build context grouped by user
        playlists_by_user = {}
        for pl in queryset:
            playlists_by_user.setdefault(pl.user, []).append(pl)

        context = {
            'opts': self.model._meta,
            'playlists_by_user': playlists_by_user,
            'queryset': queryset,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
        }

        return TemplateResponse(request, 'admin/playlist_merge_confirmation.html', context)

    merge_playlists.short_description = "Fusionner les playlists sélectionnées (par utilisateur)"



