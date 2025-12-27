from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import TrackUploadForm, VideoUploadForm
from django.db.models import Q

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.db.models import Q
from .models import Track, Video, Artist
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import stripe
import json
from django.db.models import Sum
from django.views.decorators.http import require_POST
from .utils.b2 import get_signed_url


class AlbumListView(ListView):
    model = Album
    template_name = 'store/album_list.html'
    context_object_name = 'albums'



def track_list(request):
    tracks = Track.objects.all()  # Récupérer toutes les pistes
    return render(request, 'store/track_list.html', {'tracks': tracks})


class AlbumDetailView(DetailView):
    model = Album
    template_name = 'store/album_detail.html'
    context_object_name = 'album'

class VideoListView(ListView):
    model = Video
    template_name = 'store/video_list.html'
    context_object_name = 'videos'
    paginate_by = 10

    def get_queryset(self):
        return (
        Video.objects
        .select_related("artist", "Video_Category")
        .only(
            "id", "title", "thumbnail",
            "play_count", "download_count",
            "artist_id", "Video_Category_id",
        )
        .order_by("-id")
    )


from django.views.generic import DetailView

class VideoDetailView(DetailView):
    model = Video
    template_name = "store/video_detail.html"
    context_object_name = "video"

    def get_object(self, queryset=None):
        video = super().get_object(queryset)
        # Incrément du compteur
        video.play_count += 1
        video.save(update_fields=["play_count"])
        return video

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string

def video_list_ajax(request):
    page = request.GET.get("page", 1)
    videos = Video.objects.all().order_by("-id")
    paginator = Paginator(videos, 10)

    page_obj = paginator.get_page(page)

    html = render_to_string("store/components/video_items.html", {
        "videos": page_obj.object_list
    })

    return JsonResponse({
        "html": html,
        "has_next": page_obj.has_next()
    })



class CinemaVideoListView(ListView):
    model = Video
    template_name = 'store/video_cinema.html'  # Assurez-vous que c'est bien le bon fichier
    context_object_name = 'object_list'

    def get_queryset(self):
        return Video.objects.filter(Video_Category__name="Cinéma")  # Filtrage par catégorie "Cinéma"


class LongMetrageListView(ListView):
    model = Video
    template_name = 'store/video_long_metrage.html'  # Assurez-vous que ce fichier existe
    context_object_name = 'object_list'

    def get_queryset(self):
        return Video.objects.filter(Video_Category__name="Long-métrage")  # Filtrage par catégorie

def liste_categories_musique(request):
    categories = MusicCategory.objects.all()
    print(categories)  # 🔍 Vérifie ce qui est récupéré
    return render(request, 'store/categories_music.html', {'categories': categories})

def liste_categories_videos(request):
    categories = VideoCategory.objects.all()  # Récupérer toutes les catégories de vidéos

    return render(request, 'store/categories_videos.html', {'categories': categories})

class SerieListView(ListView):
    model = Video
    template_name = 'store/video_serie.html'  # Assurez-vous que ce fichier existe
    context_object_name = 'object_list'

    def get_queryset(self):
        return Video.objects.filter(Video_Category__name="Série")  # Filtrage par catégorie

def popular_videos(request):
    # Trier les vidéos par vues (play_count) en ordre décroissant et limiter à 20
    videos = Video.objects.all().order_by('-play_count')[:20]
    return render(request, 'store/video_populaire.html', {'object_list': videos})

# # # # def play_track(request: HttpRequest, track_id: int):
# # # #     """
# # # #     Fonction pour lire un morceau et incrémenter le compteur de lecture.
# # # #     """
# # # #     track = get_object_or_404(Track, id=track_id)
# # # #     track.play_count += 1
# # # #     track.save()
# # # #     return JsonResponse({'status': 'success', 'play_count': track.play_count})


@login_required
def download_track(request: HttpRequest, track_id: int):
    """
    Fonction pour télécharger un morceau.
    """
    track = get_object_or_404(Track, id=track_id)
    track.download_count += 1
    track.save()
    response = HttpResponse(track.file.read(), content_type='audio/mpeg')
    response['Content-Disposition'] = f'attachment; filename="{track.file.name}"'
    return response

@login_required
def download_video(request: HttpRequest, video_id: int):
    """
    Fonction pour télécharger une vidéo.
    """
    video = get_object_or_404(Video, id=video_id)
    video.download_count += 1
    video.save()
    response = HttpResponse(video.file.read(), content_type='video/mp4')
    response['Content-Disposition'] = f'attachment; filename="{video.file.name}"'
    return response

def register(request: HttpRequest):
    """
    Fonction pour enregistrer un nouvel utilisateur.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def upload_track(request: HttpRequest):
    """
    Fonction pour télécharger un nouveau morceau.
    """
    if request.method == 'POST':
        form = TrackUploadForm(request.POST, request.FILES)
        if form.is_valid():
            track = form.save(commit=False)
            track.artist = request.user  # Associer l'utilisateur actuel à l'audio
            track.save()
            return redirect('track_list')  # Rediriger vers la liste des pistes après l'upload
    else:
        form = TrackUploadForm()
    return render(request, 'upload_track.html', {'form': form})

@login_required
def upload_video(request: HttpRequest):
    """
    Fonction pour télécharger une nouvelle vidéo.
    """
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.artist = request.user  # Associer l'utilisateur actuel à la vidéo
            video.save()
            return redirect('video_list')  # Rediriger vers la liste des vidéos après l'upload
    else:
        form = VideoUploadForm()
    return render(request, 'upload_video.html', {'form': form})



@login_required
def download_album(request, album_id):
    album = get_object_or_404(Album, id=album_id)

    if not album.fichier:
        raise Http404("Fichier non disponible pour cet album.")

    try:
        # Utilise le storage configuré pour ce FileField
        storage = album.fichier.storage
        signed_url = storage.url(album.fichier.name)  # génère une URL signée automatiquement

        return redirect(signed_url)
    except Exception as e:
        import traceback
        print("Erreur B2:", e)
        traceback.print_exc()
        return JsonResponse({"error": "Impossible de générer l’URL signée"}, status=500)


@login_required
def purchase_item(request: HttpRequest, item_type: str, item_id: int):
    """
    Fonction pour gérer l'achat d'un morceau ou d'une vidéo.
    """
    if item_type == 'track':
        item = get_object_or_404(Track, id=item_id)
    elif item_type == 'video':
        item = get_object_or_404(Video, id=item_id)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid item type'}, status=400)
    
    # Logique de paiement ici (intégration avec Stripe ou autre)

    # Si le paiement est réussi, enregistrer l'achat
    Purchase.objects.create(
        user=request.user,
        track=item if item_type == 'track' else None,
        video=item if item_type == 'video' else None
    )
    
    return redirect('store:album_list')  # Rediriger vers la liste des albums après l'achat

# Définition du décorateur pour vérifier si l'utilisateur est un artiste
def artist_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        # Vérifie si l'utilisateur a un lien avec le modèle Artist
        if not Artist.objects.filter(user=request.user).exists():
            return redirect('not_authorized')  # Redirige si l'utilisateur n'est pas un artiste
        return view_func(request, *args, **kwargs)
    return wrapper_func

def not_authorized(request):
    return render(request, 'not_authorized.html')


def homepage(request):
    popular_artists = Artist.objects.filter(is_popular=True)[:10]  # Filtre pour les artistes populaires
    popular_albums = Album.objects.filter(is_popular=True)[:5]    # Filtre pour les albums populaires
    popular_videos = Video.objects.filter(is_popular=True)[:5]    # Filtre pour les vidéos populaires
    music_categories = MusicCategory.objects.all()                # Toutes les catégories de musique
    video_categories = VideoCategory.objects.all()                # Toutes les catégories de vidéo

    context = {
        'popular_artists': popular_artists,
        'popular_albums': popular_albums,
        'popular_videos': popular_videos,
        'music_categories': music_categories,
        'video_categories': video_categories
    }

    return render(request, 'store/homepage.html', context)

@login_required
def create_artist(request):
    if request.method == 'POST':
        form = ArtistForm(request.POST, request.FILES)
        if form.is_valid():
            artist = form.save(commit=False)
            if request.user.is_superuser:  # Si l'utilisateur est un superuser, il peut ne pas être lié à un user spécifique
                artist.user = None
            artist.save()
            return redirect('artist_list')
    else:
        form = ArtistForm()
    return render(request, 'create_artist.html', {'form': form})



@require_GET
def recherche_globale(request):
    query = request.GET.get("q", "").strip()
    data = {"tracks": [], "videos": [], "artists": [], "albums": []}

    if not query:  # si aucun caractère
        return JsonResponse(data)

    # Tracks
    tracks = Track.objects.filter(
        Q(title__icontains=query) |
        Q(artist__name__icontains=query) |
        Q(album__title__icontains=query)
    ).select_related("artist", "album")[:20]

    # Videos
    videos = Video.objects.filter(
        Q(title__icontains=query) |
        Q(artist__name__icontains=query) |
        Q(description__icontains=query)
    ).select_related("artist")[:20]

    # Artists
    artists = Artist.objects.filter(
        Q(name__icontains=query) |
        Q(bio__icontains=query)
    )[:20]

    # Albums
    albums = Album.objects.filter(
        Q(title__icontains=query) |
        Q(artist__name__icontains=query)
    ).select_related("artist")[:20]

    # Format JSON
    data["tracks"] = [
        {
            "id": t.id,
            "title": t.title,
            "artist": getattr(t.artist, "name", "Inconnu"),
            "album": getattr(t.album, "title", ""),
            "audio_url": t.file_url or "",  # ✅ helper → URL signée ou vide
            "cover_image": t.cover_url or static("img/trackdefault.png"),  # ✅ fallback
        }
        for t in tracks
    ]

    data["videos"] = [
        {
            "id": v.id,
            "title": v.title,
            "artist": getattr(v.artist, "name", "Inconnu"),
            "url": reverse("video_detail", args=[v.id]),  # ✅ lien robuste
            "thumbnail": v.cover_url or static("img/videodefault.png"),
            "file_url": v.file_url or "",  # ✅ URL signée ou vide
        }
        for v in videos
    ]

    data["artists"] = [
        {
            "id": a.id,
            "name": a.name,
            "url": reverse("artist_detail", args=[a.id]),
            "image": a.image_url or static("img/artistedefault.png"),
        }
        for a in artists
    ]

    data["albums"] = [
        {
            "id": alb.id,
            "title": alb.title,
            "artist": getattr(alb.artist, "name", "Inconnu"),
            "url": reverse("album_detail", args=[alb.id]),
            "cover_image": alb.cover_url or static("img/default-album.png"),
            "fichier_url": alb.fichier_url or "",  # ✅ URL signée ou vide
        }
        for alb in albums
    ]

    return JsonResponse(data)




def artist_detail(request, pk):
    artist = get_object_or_404(Artist, pk=pk)
    musiques = Track.objects.filter(artist=artist)
    videos = Video.objects.filter(artist=artist)
    return render(request, "store/artist_detail.html", {
        'artist': artist,
        'musiques': musiques,
        'videos': videos,
    })


def recherche_resultat(request):
    query = request.GET.get("q", "")
    musiques = Track.objects.filter(Q(title__icontains=query) | Q(artist__name__icontains=query))
    videos = Video.objects.filter(Q(title__icontains=query) | Q(artist__name__icontains=query))
    artistes = Artist.objects.filter(name__icontains=query)
    albums = Album.objects.filter(title__icontains=query)

    context = {
        "musiques": musiques,
        "videos": videos,
        "artistes": artistes,
        "albums": albums,
    }
    return render(request, "store/recherche_resultat.html", context)


@require_POST
def play_video_increment(request: HttpRequest, video_id: int):
    """
    Fonction pour lire une vidéo et incrémenter le compteur de lecture.
    """
    video = get_object_or_404(Video, id=video_id)
    video.play_count += 1
    video.save(update_fields=['play_count'])
    return JsonResponse({'status': 'success', 'play_count': video.play_count})

def play_video(request: HttpRequest, video_id: int):
    video = get_object_or_404(Video, id=video_id)
    video.play_count += 1
    video.save()
    artist_videos = Video.objects.filter(artist=video.artist).exclude(id=video.id)

    return render(request, 'store/play_video.html', {
        'video': video,
        'artist_videos': artist_videos,
        })

def play_track(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    
    # Récupère tous les tracks de l'album
    tracks = Track.objects.filter(album=track.album).values(
        'id', 'title', 'artist__name', 'duration', 'file', 'cover_image'
    )
    tracks_list = list(tracks)

    # Optional: if a playlist_id is provided in the querystring, try to show
    # the tracks from that playlist. Otherwise prepare suggested tracks the user
    # may like (same artist or recent tracks).
    playlist_tracks_list = None
    suggested_tracks = []
    playlist_id = request.GET.get('playlist_id')
    if playlist_id:
        try:
            # only allow user's own playlists for safety
            pl = Playlist.objects.get(id=playlist_id, user=request.user)
            pls = pl.tracks.all().values('id', 'title', 'artist__name', 'duration', 'file', 'cover_image')
            playlist_tracks_list = list(pls)
        except Exception:
            playlist_tracks_list = None

    if not playlist_tracks_list:
        # Suggest tracks: prefer same artist, otherwise recent tracks
        same_artist = Track.objects.filter(artist=track.artist).exclude(id=track.id).values(
            'id', 'title', 'artist__name', 'duration', 'file', 'cover_image'
        )[:6]
        suggested_tracks = list(same_artist)
        if not suggested_tracks:
            recent = Track.objects.exclude(id=track.id).order_by('-id').values(
                'id', 'title', 'artist__name', 'duration', 'file', 'cover_image'
            )[:6]
            suggested_tracks = list(recent)

    context = {
        'track': track,
        'tracks': tracks_list,
        'playlist_tracks': playlist_tracks_list,
        'suggested_tracks': suggested_tracks,
    }
    return render(request, 'store/play_track.html', context)



@login_required
def like_track(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    if request.user in track.liked_by.all():
        track.liked_by.remove(request.user)  # retirer le like
    else:
        track.liked_by.add(request.user)     # ajouter le like
    return JsonResponse({'likes_count': track.liked_by.count()})

@login_required
def add_to_playlist(request, track_id, playlist_id):
    track = get_object_or_404(Track, id=track_id)
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    playlist.tracks.add(track)
    return JsonResponse({'status': 'success'})

@login_required
def user_playlists(request):
    playlists = Playlist.objects.filter(user=request.user)
    data = [{"id": p.id, "name": p.name} for p in playlists]
    return JsonResponse(data, safe=False)



from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_POST

@login_required
@require_POST
def toggle_like_follow(request, model_name, object_id):
    model_map = {
        'track': Track,
        'video': Video,
        'artist': Artist
    }
    model_class = model_map.get(model_name)
    if not model_class:
        return JsonResponse({'error': 'Modèle invalide'}, status=400)

    obj = get_object_or_404(model_class, id=object_id)
    content_type = ContentType.objects.get_for_model(obj)

    action, created = UserAction.objects.get_or_create(
        user=request.user,
        action_type='like' if model_name != 'artist' else 'follow',
        content_type=content_type,
        object_id=obj.id
    )

    if not created:
        action.delete()
        status = False
    else:
        status = True

    return JsonResponse({'status': status})


@login_required
@require_POST
def add_track_to_playlist(request, playlist_id, track_id):
    track = get_object_or_404(Track, id=track_id)
    playlist = get_object_or_404(Playlist, id=playlist_id, user=request.user)
    playlist.tracks.add(track)
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def create_playlist(request):
    import json
    data = json.loads(request.body)
    name = data.get("name")
    if not name:
        return JsonResponse({"status": "error", "message": "Nom manquant"}, status=400)
    # Vérifier l'unicité du nom pour cet utilisateur
    if Playlist.objects.filter(user=request.user, name__iexact=name).exists():
        return JsonResponse({"status": "error", "message": "Vous avez déjà une playlist avec ce nom."}, status=400)

    pl = Playlist.objects.create(user=request.user, name=name)
    return JsonResponse({"status": "success", "id": pl.id, "name": pl.name})




def user_playlists_or_suggestions(request):
    if request.user.is_authenticated:
        playlists = Playlist.objects.filter(user=request.user)
        data = {
            "is_authenticated": True,
            "playlists": [{"id": p.id, "name": p.name} for p in playlists]
        }
    else:
        # Suggestions : 5 tracks aléatoires
        suggestions = Track.objects.order_by('?')[:5]
        data = {
            "is_authenticated": False,
            "suggestions": [
                {"id": t.id, "title": t.title, "artist": t.artist.name}
                for t in suggestions
            ]
        }
    return JsonResponse(data)


@login_required
def user_library(request):
    playlists = Playlist.objects.filter(user=request.user)
    artists = Artist.objects.filter(is_popular=True)[:10]
    albums = Album.objects.filter(is_popular=True)[:10]
    
    return render(request, 'store/library_sidebar.html', {
        'playlists': playlists,
        'artists': artists,
        'albums': albums,
    })


@login_required
def library_data(request):
    playlists = Playlist.objects.filter(user=request.user).values("id", "name")
    artists = Artist.objects.filter(is_popular=True).values("id", "name", "image")
    albums = Album.objects.filter(is_popular=True).values("id", "title", "artist__name", "cover_image")

    return JsonResponse({
        "playlists": list(playlists),
        "artists": list(artists),
        "albums": list(albums),
    })

@login_required
def profile(request):
    from Utilisateurs.models import Profile
    from .forms import ProfileForm, ArtistProfileForm

    # Vérifier si l'utilisateur est un artiste
    try:
        artist = Artist.objects.get(user=request.user)
        is_artist = True
    except Artist.DoesNotExist:
        artist = None
        is_artist = False

    # Récupérer ou créer le profil utilisateur
    profile_obj, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if is_artist:
            form = ArtistProfileForm(request.POST, request.FILES, instance=artist)
        else:
            form = ProfileForm(request.POST, request.FILES, instance=profile_obj)

        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        if is_artist:
            form = ArtistProfileForm(instance=artist)
        else:
            form = ProfileForm(instance=profile_obj)

    context = {
        'is_artist': is_artist,
        'artist': artist,
        'profile': profile_obj,
        'form': form,
    }

    if is_artist:
        # Ajouter des données spécifiques à l'artiste
        tracks = Track.objects.filter(artist=artist)
        albums = Album.objects.filter(artist=artist)
        videos = Video.objects.filter(artist=artist)
        context.update({
            'tracks': tracks,
            'albums': albums,
            'videos': videos,
        })
        template = 'store/profile_artist.html'
    else:
        # Ajouter des données spécifiques au client
        playlists = Playlist.objects.filter(user=request.user)
        liked_tracks = Track.objects.filter(liked_by=request.user)
        context.update({
            'playlists': playlists,
            'liked_tracks': liked_tracks,
        })
        template = 'store/profile_client.html'

    return render(request, template, context)

# store/views.py


# ✅ Ajouter un album au panier
# Exemple d'ajout dans le panier


def ajouter_au_panier(request, pk):
    if request.method == "POST":
        quantite = int(request.POST.get("quantite", 1))

        try:
            album = Album.objects.get(pk=pk)
        except Album.DoesNotExist:
            return JsonResponse({"success": False, "error": "Album non trouvé"})

        # Ajout au panier via session
        panier = request.session.get('panier', {})
        if str(pk) in panier:
            # Album déjà dans le panier, ne pas ajouter et afficher un message
            return JsonResponse({"success": False, "error": "Cet album est déjà dans votre panier."})

        # Ajouter seulement si pas déjà présent
        panier[str(pk)] = {
            'titre': album.title,
            'prix': float(album.price),
            'quantite': quantite,
            'image': album.cover_image.url if album.cover_image else '/static/img/trackdefault.png'
        }
        request.session['panier'] = panier

        # Renvoie le nouveau total
        total_count = sum(item['quantite'] for item in panier.values())
        return JsonResponse({"success": True, "count": total_count})

    return JsonResponse({"success": False, "error": "Requête invalide"})







@csrf_exempt  # pour test, on enlèvera après
def retirer_du_panier(request, album_id):
    if request.method == "POST":
        panier = request.session.get('panier', {})
        album_id_str = str(album_id)

        if album_id_str in panier:
            del panier[album_id_str]
            request.session['panier'] = panier

            # Recalculer le total
            total_general = sum(item['prix'] * item['quantite'] for item in panier.values())
            total_count = sum(item['quantite'] for item in panier.values())

            return JsonResponse({"success": True, "total": f"{total_general:.2f} €", "count": total_count})
        else:
            return JsonResponse({"success": False, "error": "Album non trouvé dans le panier."})

    return JsonResponse({"success": False, "error": "Méthode non autorisée."})



# ✅ Vider le panier
def vider_panier(request):
    request.session['panier'] = {}
    return redirect('panier')


# ✅ Afficher le panier
def panier(request):
    # Récupérer le panier depuis la session (ou créer vide)
    panier = request.session.get('panier', {})
    produits = []
    total_general = 0

    for pk, item in panier.items():
        # Récupérer le produit réel depuis la base pour s'assurer des données
        try:
            album = Album.objects.get(pk=pk)
            image_url = album.cover_image.url if album.cover_image else '/static/img/trackdefault.png'
        except Album.DoesNotExist:
            image_url = '/static/img/trackdefault.png'

        # Sécuriser les clés pour les anciens items
        prix = item.get('prix', float(album.price if 'album' in locals() else 0))
        titre = item.get('titre', album.title if 'album' in locals() else 'Inconnu')
        quantite = item.get('quantite', 1)

        total = prix * quantite
        total_general += total

        produits.append({
            'id': pk,
            'nom': titre,
            'prix': prix,
            'quantite': quantite,
            'total': total,
            'image': image_url

        })

    return render(request, 'store/panier.html', {
        'produits': produits,
        'total_general': total_general
    })


# ✅ Acheter et permettre le téléchargement
def acheter(request):
    panier = request.session.get('panier', {})
    if not panier:
        messages.warning(request, "Votre panier est vide.")
        return redirect('panier')

    # Exemple : ici on simule l'achat (sans paiement réel)
    request.session['panier'] = {}  # on vide après achat
    messages.success(request, "✅ Achat réussi ! Vos albums sont prêts à être téléchargés.")
    return redirect('panier')


# ✅ Télécharger un album après achat
def telecharger_album(request, pk):
    album = get_object_or_404(Album, pk=pk)
    if not album.fichier:
        raise Http404("Fichier non disponible pour cet album.")
    return FileResponse(album.fichier.open('rb'), as_attachment=True, filename=f"{album.title}.zip")


@csrf_exempt
def create_payment_intent(request):
    import os
    from django.conf import settings

    stripe.api_key = settings.REMOVED

    panier = request.session.get('panier', {})
    total = sum(item['prix'] * item['quantite'] for item in panier.values())

    try:
        intent = stripe.PaymentIntent.create(
            amount=int(total * 100),  # montant total en centimes
            currency="eur",
            automatic_payment_methods={"enabled": True},
        )
        return JsonResponse({"client_secret": intent.client_secret})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)



@csrf_exempt
def paiement_stripe(request):
    if request.method == "POST":
        data = json.loads(request.body)
        montant = data.get("montant")

        # 🔹 Simulation (à remplacer par vraie API Stripe)
        if montant and float(montant) > 0:
            return JsonResponse({"success": True, "message": "Paiement Stripe réussi."})
        return JsonResponse({"success": False, "message": "Montant invalide."})

@csrf_exempt
def paiement_paypal(request):
    if request.method == "POST":
        data = json.loads(request.body)
        montant = data.get("montant")

        # 🔹 Simulation PayPal
        if montant and float(montant) > 0:
            return JsonResponse({"success": True, "message": "Paiement PayPal réussi."})
        return JsonResponse({"success": False, "message": "Montant invalide."})
def stripe_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return HttpResponse("No session")
    session = stripe.checkout.Session.retrieve(session_id, expand=['line_items'])
    # vérifie payment_status == 'paid' puis créer commande, générer liens etc.
    return render(request, "payments/success.html", {"session": session})




# ===================== INITIATION PAIEMENT =====================
@csrf_exempt
def paiement_mobile(request, operateur):
    if request.method == "POST":
        data = json.loads(request.body)
        numero = data.get("numero")
        montant = data.get("montant")
        commande_id = data.get("commande_id")

        # Ici tu peux récupérer la commande depuis la DB
        try:
            commande = Commande.objects.get(id=commande_id)
        except Commande.DoesNotExist:
            return JsonResponse({"error": "Commande introuvable"}, status=404)

        # Exemple d'envoi au fournisseur Mobile Money (simulé)
        # Remplace par ton vrai code marchand et API opérateur
        if operateur == "orange":
            code_marchand = "TON_CODE_MARCHAND_ORANGE"
        elif operateur == "moov":
            code_marchand = "TON_CODE_MARCHAND_MOOV"
        elif operateur == "wave":
            code_marchand = "TON_CODE_MARCHAND_WAVE"
        else:
            return JsonResponse({"error":"Opérateur inconnu"}, status=400)

        # Ici tu devrais appeler l'API Mobile Money du Mali pour initier le paiement
        # On simule la réponse
        print(f"Initiation paiement {operateur}: numero={numero}, montant={montant}, code_marchand={code_marchand}")

        # Stocker état de paiement "en attente"
        commande.etat_paiement = "en_attente"
        commande.save()

        return JsonResponse({"message": f"Paiement {operateur} initié. Vérifiez votre téléphone."})

    return JsonResponse({"error":"Méthode non autorisée"}, status=405)

# ===================== CALLBACK PAIEMENT =====================
@csrf_exempt
def callback_mobile(request, operateur):
    """
    Endpoint que l'opérateur Mobile Money appellera pour confirmer le paiement
    """
    if request.method == "POST":
        data = json.loads(request.body)
        commande_id = data.get("commande_id")
        status = data.get("status")  # 'success' ou 'failed'

        try:
            commande = Commande.objects.get(id=commande_id)
        except Commande.DoesNotExist:
            return JsonResponse({"error":"Commande introuvable"}, status=404)

        if status == "success":
            commande.etat_paiement = "payé"
        else:
            commande.etat_paiement = "échoué"

        commande.save()
        return JsonResponse({"message": f"Paiement {operateur} {status}"})

    return JsonResponse({"error":"Méthode non autorisée"}, status=405)


def panier_count(request):
    panier = request.session.get('panier', {})
    total = sum(item['quantite'] for item in panier.values())
    return JsonResponse({'count': total})


def artist_profile(request, artist_id):
    profile_user = get_object_or_404(User, id=artist_id)
    artist = getattr(profile_user, "artist", None)  # None si pas artiste
    playlists = profile_user.playlists.all()

    # Gestion de l'upload d'avatar si c'est l'utilisateur connecté
    if request.method == "POST" and request.user == profile_user:
        avatar_file = request.FILES.get("avatar")
        if avatar_file:
            profile_user.avatar = avatar_file
            profile_user.save()
            return redirect('artist_profile', artist_id=artist_id)  # refresh après upload

    # Suivi
    is_following = False
    if request.user.is_authenticated and request.user != profile_user and artist:
        is_following = Follow.objects.filter(
            follower=request.user,
            artist=artist
        ).exists()

    context = {
        "profile_user": profile_user,
        "artist": artist,
        "tracks": artist.tracks.all() if artist else [],
        "albums": artist.albums.all() if artist else [],
        "videos": artist.videos.all() if artist else [],
        "playlists": playlists,
        "is_following": is_following,
    }
    return render(request, "store/artist_profile.html", context)

def user_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    playlists = profile_user.playlists.all()  # playlists de l'utilisateur

    context = {
        "profile_user": profile_user,
        "playlists": playlists,
    }
    return render(request, "store/user_profile.html", context)

def profile_view(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    is_following = request.user.is_authenticated and request.user.is_following(profile_user)
    return render(request, 'store/profile.html', {
        'profile_user': profile_user,
        'is_following': is_following,
    })

@login_required
def follow(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    request.user.following.add(user_to_follow)
    return JsonResponse({"status": "ok"})

@login_required
def unfollow(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    request.user.following.remove(user_to_unfollow)
    return JsonResponse({"status": "ok"})




def library_api(request):
    data = {"message": "API OK"}
    return JsonResponse(data)



from django.core.files.storage import default_storage
from store.media_converter import convert_audio_to_opus
import tempfile

def handle_audio_upload(file):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        for chunk in file.chunks():
            tmp.write(chunk)
        tmp_path = tmp.name

    converted = convert_audio_to_opus(tmp_path)

    with open(converted, "rb") as f:
        path = default_storage.save(
            f"audio/{converted.name}",
            f
        )

    return path
