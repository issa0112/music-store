# store/storage_backends.py
import logging
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import FileSystemStorage
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Storage local fallback
local_storage = FileSystemStorage(location=settings.MEDIA_ROOT)

class FallbackMediaStorage(S3Boto3Storage):
    location = ''  # racine du bucket
    file_overwrite = False

    def _open(self, name, mode='rb'):
        """
        Essaie d'ouvrir le fichier depuis B2.
        Si impossible, utilise le stockage local.
        """
        try:
            return super()._open(name, mode)
        except ClientError as e:
            logger.warning(f"Backblaze B2 inaccessible pour {name}, fallback local: {e}")
            return local_storage._open(name, mode)

    def _save(self, name, content):
        """
        Sauvegarde le fichier sur B2 et en local.
        """
        # Sauvegarde locale
        local_storage._save(name, content)
        try:
            result = super()._save(name, content)
            logger.info(f"Uploaded {name} to Backblaze B2 successfully")
            return result
        except ClientError as e:
            logger.error(f"Failed to upload {name} to Backblaze B2: {e}")
            # Si échec, on garde juste la version locale
            return name
MediaStorage = FallbackMediaStorage