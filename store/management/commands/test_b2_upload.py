from django.core.management.base import BaseCommand
from django.core.files import File
from store.storage_backends import FallbackMediaStorage

class Command(BaseCommand):
    help = 'Test upload fichier sur B2 et local'

    def handle(self, *args, **kwargs):
        storage = FallbackMediaStorage()
        filename = 'test_upload.txt'

        with open('media/test_b2.txt', 'rb') as f:
            file_obj = File(f)
            storage.save(filename, file_obj)

        self.stdout.write(self.style.SUCCESS(f'Fichier "{filename}" uploadé avec succès !'))
