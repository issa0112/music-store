from django.urls import path
from . import views

urlpatterns = [
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion_compte/', views.deconnecter_compte, name='deconnexion_compte'),
    path('profil/',views.profile_view, name='profile'),  # Vérifie bien le nom ici
]
