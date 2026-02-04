from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re
from django.contrib import messages
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse



def deconnecter_compte(request):
    if request.method == "POST":
        logout(request)
        return JsonResponse({'success': True, 'message': 'Déconnexion réussie.'})
    return JsonResponse({'success': False, 'message': 'Méthode de requête non valide.'})




from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

@csrf_protect
def connexion(request):
    # POST = login via AJAX
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            return JsonResponse({"success": False, "message": "Tous les champs sont requis"}, status=400)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "message": "Identifiants incorrects"}, status=400)

    # GET = formulaire classique
    next_url = request.GET.get("next", "")
    # Si AJAX GET → renvoyer JSON vide, sinon afficher le formulaire HTML
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return JsonResponse({"success": False, "message": "Méthode GET non autorisée"}, status=405)

    return render(request, "login.html", {"next": next_url})





@csrf_protect
def inscription(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if not all([username, email, password, password_confirm]):
            return JsonResponse({"success": False, "message": "Tous les champs sont requis."}, status=400)

        if password != password_confirm:
            return JsonResponse({"success": False, "message": "Les mots de passe ne correspondent pas."}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"success": False, "message": "Nom d'utilisateur déjà pris."}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({"success": False, "message": "Adresse email déjà utilisée."}, status=400)

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        return JsonResponse({"success": True, "message": "Inscription réussie."})

    return JsonResponse({"success": False, "message": "Méthode non autorisée."}, status=405)

# views.py

def profile_view(request, user_id=None):
    # Si tu veux afficher le profil d’un autre utilisateur
    if user_id:
        profile_user = User.objects.get(id=user_id)
    else:
        profile_user = request.user

    profile = profile_user.profile

    playlists = getattr(profile_user, 'playlists', []).all() if hasattr(profile_user, 'playlists') else []
    liked_tracks = profile.liked_tracks.all()
    following = profile.following.all()

    return render(request, 'store/profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'playlists': playlists,
        'liked_tracks': liked_tracks,
        'following': following,
    })

