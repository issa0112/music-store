import os
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

class Command(BaseCommand):
    help = "Vérifie la configuration Backblaze B2 et fallback local"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("🔍 Vérification du stockage..."))

        try:
            # Upload test
            filename = "diagnostic_b2.txt"
            content = ContentFile(b"Hello depuis la commande check_b2")
            default_storage.save(filename, content)

            # Existence
            exists = default_storage.exists(filename)
            self.stdout.write(f"✅ Fichier créé : {exists}")

            # URL
            url = default_storage.url(filename)
            self.stdout.write(f"🌐 URL générée : {url}")

            # Lecture
            f = default_storage.open(filename)
            data = f.read()
            self.stdout.write(f"📄 Contenu lu : {data.decode()}")

            self.stdout.write(self.style.SUCCESS("Diagnostic terminé avec succès !"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erreur lors du diagnostic : {e}"))
