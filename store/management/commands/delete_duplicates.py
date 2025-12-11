import os
import hashlib
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Supprime les fichiers doublons dans MEDIA_ROOT.'

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            self.stdout.write(self.style.ERROR(f"MEDIA_ROOT n'existe pas: {media_root}"))
            return

        self.stdout.write(f"Scan de {media_root} pour doublons...")

        hashes = {}
        duplicates = []

        # Parcourt tous les fichiers dans MEDIA_ROOT (y compris sous-dossiers)
        for root, dirs, files in os.walk(media_root):
            for file in files:
                file_path = os.path.join(root, file)

                # Calcule un hash du fichier pour détecter les doublons exacts
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()

                if file_hash in hashes:
                    duplicates.append(file_path)
                else:
                    hashes[file_hash] = file_path

        # Supprime les doublons détectés
        for dup in duplicates:
            os.remove(dup)
            self.stdout.write(self.style.WARNING(f"Doublon supprimé: {dup}"))

        self.stdout.write(self.style.SUCCESS(f"Terminé ! {len(duplicates)} doublons supprimés."))
