import os
import django

# 1️⃣ Configurer Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music_store.settings")
django.setup()

# 2️⃣ Importer ton stockage **après** setup
from store.storage_backends import FallbackMediaStorage
from django.core.files.base import ContentFile
import os

# Instancier ton stockage (B2 + local)
storage = FallbackMediaStorage()

# Nom du fichier de test
filename = "test_upload_local.txt"
content = ContentFile(b"Ceci est un test d'upload en local et B2.")

# Upload
try:
    path = storage.save(filename, content)
    print(f"Fichier '{path}' uploadé avec succès !")
except Exception as e:
    print("Erreur lors de l'upload :", e)

# Vérifier la présence locale
local_path = os.path.join(os.getenv("MEDIA_ROOT", "media"), filename)
if os.path.exists(local_path):
    print(f"Fichier trouvé localement : {local_path}")
else:
    print("Fichier non trouvé localement.")
