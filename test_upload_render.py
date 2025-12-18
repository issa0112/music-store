# test_upload_render.py
import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music_store.settings")
django.setup()

from django.core.files.storage import default_storage

# Crée un fichier virtuel en mémoire
content = b"Ceci est un test d'upload depuis Render"
file_name = "uploads/test_upload_render.txt"
file_content = ContentFile(content)

# Upload via le backend par défaut (FallbackMediaStorage)
saved_name = default_storage.save(file_name, file_content)
print(f"Fichier '{saved_name}' uploadé avec succès !")
