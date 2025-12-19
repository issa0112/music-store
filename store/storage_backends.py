# store/storage_backends.py
import logging
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Stockage local
local_storage = FileSystemStorage(location=settings.MEDIA_ROOT)

class FallbackMediaStorage(S3Boto3Storage):
    """
    Essaie d'utiliser Backblaze B2.
    Si B2 est indisponible, bascule sur le stockage local.
    """
    location = ''
    file_overwrite = False

    def _save(self, name, content):
        try:
            # Tentative d'upload sur B2
            result = super()._save(name, content)
            logger.info(f"✅ Fichier {name} envoyé sur B2 avec succès")
            return result
        except ClientError as e:
            logger.error(f"❌ Échec upload B2 pour {name}, fallback local: {e}")
            return local_storage._save(name, content)

    def _open(self, name, mode='rb'):
        try:
            # Tentative de lecture depuis B2
            return super()._open(name, mode)
        except ClientError as e:
            logger.warning(f"⚠️ Lecture B2 échouée pour {name}, fallback local: {e}")
            return local_storage._open(name, mode)

    def exists(self, name):
        """
        Vérifie d'abord sur B2, sinon en local.
        """
        try:
            return super().exists(name)
        except ClientError:
            return local_storage.exists(name)
