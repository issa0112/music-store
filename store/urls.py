from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('album/', AlbumListView.as_view(), name='album_list'),
    path('albums/<int:pk>/', AlbumDetailView.as_view(), name='album_detail'),
    path('videos/', VideoListView.as_view(), name='video_list'),
    path("videos/ajax/", video_list_ajax, name="video_list_ajax"),
    path("videos/<int:pk>/", VideoDetailView.as_view(), name="video_detail"),

    path('track/play/<int:track_id>/', play_track, name='play_track'),
    path('video/play/<int:video_id>/', play_video, name='play_video'),
    path('purchase/<str:item_type>/<int:item_id>/', purchase_item, name='purchase_item'),
    path('track/download/<int:track_id>/', download_track, name='download_track'),
    path('video/download/<int:video_id>/', download_video, name='download_video'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),

    path('track/upload/', upload_track, name='upload_track'),
    path('video/upload/', upload_video, name='upload_video'),
    path('not_authorized/', not_authorized, name='not_authorized'),
    path('', homepage, name='homepage'),
    path('tracks/', track_list, name='track_list'),
    path('recherche/', recherche_globale, name='recherche_globale'),
    path('cinema-videos/', CinemaVideoListView.as_view(), name='cinema_videos'),
    path('cinema-videos/long-metrage/', LongMetrageListView.as_view(), name='long_metrage_videos'),
    path('cinema-videos/serie/', SerieListView.as_view(), name='serie_videos'),
    path('videos-populaires/', popular_videos, name='videos_populaires'),
    path('categories-musique/', liste_categories_musique, name='categories_musique'),
    path('categories-videos/', liste_categories_videos, name='categories_videos'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('artist/<int:pk>/', artist_detail, name='artist_detail'),
    path("recherche-resultat/", recherche_resultat, name="recherche_resultat"),
    path('video/play/<int:pk>/', play_video, name='video_detail'),
    path("playlists/user_playlists/", user_playlists, name="user_playlists"),
    path('playlists/create/', create_playlist, name='create_playlist'),
    path('playlists/<int:playlist_id>/add/<int:track_id>/', add_track_to_playlist, name='add_track_to_playlist'),
    path('action/<str:model_name>/<int:object_id>/', toggle_like_follow, name='toggle_like_follow'),
    path("playlists/popup_content/", user_playlists_or_suggestions, name="popup_content"),
    path('library/data/', library_data, name='library_data'),
    path('profile/', profile, name='profile'),
    # path('album/<int:pk>/acheter/', acheter_album, name='acheter_album'),
    path('panier/', panier, name='panier'),
    path('panier/ajouter/<int:pk>/', ajouter_au_panier, name='ajouter_au_panier'),
    path("panier/retirer/<int:album_id>/", retirer_du_panier, name="retirer_du_panier"),
    path('panier/vider/', vider_panier, name='vider_panier'),
    path('acheter/', acheter, name='acheter'),
    path('telecharger/<int:pk>/', telecharger_album, name='telecharger_album'),
    path('create-payment-intent/', create_payment_intent, name='create_payment_intent'),
    path('paiement/stripe/', paiement_stripe, name='paiement_stripe'),
    path('paiement/paypal/', paiement_paypal, name='paiement_paypal'),
    path('paiement_mobile/<str:operateur>/', paiement_mobile, name='paiement_mobile'),
    path('callback_mobile/<str:operateur>/', callback_mobile, name='callback_mobile'),
    path('panier/count/', panier_count, name='panier_count'),
    path('videos/<int:video_id>/increment_play/', play_video_increment, name='increment_play'),
    # path('profile/<int:artist_id>/', artist_profile, name='artist_profile')
    path('profile/user/<int:user_id>/', user_profile, name='user_profile'),
    path('profile/artist/<int:artist_id>/', artist_profile, name='artist_profile'),







]

if settings.DEBUG:  # Ajouter ce bloc pour servir les fichiers médias pendant le développement
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

