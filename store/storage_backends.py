import logging
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage   # <-- IMPORT MANQUANT
from botocore.exceptions import ClientError
class FallbackMediaStorage(S3Boto3Storage):
    location = ''
    file_overwrite = False

    def _save(self, name, content):
        try:
            result = super()._save(name, content)
            logger.info(f"✅ Fichier {name} envoyé sur B2 avec succès")
            return result
        except ClientError as e:
            logger.error(f"❌ Échec upload B2 pour {name}, fallback local: {e}")
            return local_storage._save(name, content)

    def _open(self, name, mode='rb'):
        try:
            return super()._open(name, mode)
        except ClientError as e:
            logger.warning(f"⚠️ Lecture B2 échouée pour {name}, fallback local: {e}")
            return local_storage._open(name, mode)

    def exists(self, name):
        try:
            return super().exists(name)
        except ClientError:
            return local_storage.exists(name)

    def url(self, name):
        """
        Génère une URL signée pour les fichiers B2 privés.
        Si B2 est indisponible, retourne l'URL locale.
        """
        try:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"),
                region_name=os.getenv("AWS_S3_REGION_NAME"),
            )
            return s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": os.getenv("AWS_STORAGE_BUCKET_NAME"), "Key": name},
                ExpiresIn=3600,  # valable 1h
            )
        except ClientError as e:
            logger.warning(f"⚠️ URL signée B2 échouée pour {name}, fallback local: {e}")
            return local_storage.url(name)

# Alias pour compatibilité avec l'ancien code
MediaStorage = FallbackMediaStorage
