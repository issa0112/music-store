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



from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
import json

@csrf_protect
def connexion(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return JsonResponse({"success": True, "message": "Connexion réussie."})
        else:
            return JsonResponse({"success": False, "message": "Nom d'utilisateur ou mot de passe incorrect."}, status=400)
    
    return JsonResponse({"message": "Méthode non autorisée."}, status=405)



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

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def profile_view(request):
    # Rediriger vers la vue de profil dans store
    return redirect('store:profile')

