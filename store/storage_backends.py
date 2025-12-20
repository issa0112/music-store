# import os
# import logging
# import boto3
# from botocore.exceptions import ClientError
# from django.conf import settings
# from django.core.files.storage import FileSystemStorage
# from storages.backends.s3boto3 import S3Boto3Storage

# # Configuration du logger
# logger = logging.getLogger(__name__)

# # Stockage local fallback (configurable via settings)
# LOCAL_MEDIA_ROOT = getattr(settings, "MEDIA_LOCAL_ROOT", os.path.join(settings.BASE_DIR, "media_local"))
# local_storage = FileSystemStorage(location=LOCAL_MEDIA_ROOT)

# class FallbackMediaStorage(S3Boto3Storage):
#     """
#     Stockage principal sur Backblaze B2 (via S3Boto3Storage),
#     avec fallback local en cas d'erreur.
#     Génère toujours des URLs signées pour B2, sinon URL locale.
#     """
#     location = ''
#     file_overwrite = False
#     default_acl = None  # Bucket privé

#     def _save(self, name, content):
#         try:
#             result = super()._save(name, content)
#             logger.info(f"✅ Fichier {name} envoyé sur B2 avec succès")
#         except Exception as e:  # élargi à toutes exceptions
#             logger.error(f"❌ Échec upload B2 pour {name}, fallback local: {e}")
#             result = local_storage._save(name, content)

#         # Copier systématiquement en local si non déjà présent
#         try:
#             if not local_storage.exists(name):
#                 content.seek(0)
#                 local_storage._save(name, content)
#                 logger.info(f"✅ Fichier {name} copié localement")
#         except Exception as e:
#             logger.warning(f"⚠️ Échec sauvegarde locale pour {name}: {e}")

#         return result

#     def _open(self, name, mode='rb'):
#         try:
#             return super()._open(name, mode)
#         except Exception as e:
#             logger.warning(f"⚠️ Lecture B2 échouée pour {name}, fallback local: {e}")
#             return local_storage._open(name, mode)

#     def exists(self, name):
#         try:
#             return super().exists(name)
#         except Exception:
#             return local_storage.exists(name)

#     def url(self, name):
#         """
#         Génère une URL signée B2 pour les fichiers privés.
#         Si B2 est indisponible, retourne l'URL locale.
#         """
#         try:
#             s3 = boto3.client(
#                 "s3",
#                 aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
#                 aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
#                 endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"),
#                 region_name=os.getenv("AWS_S3_REGION_NAME"),
#             )
#             return s3.generate_presigned_url(
#                 "get_object",
#                 Params={"Bucket": os.getenv("AWS_STORAGE_BUCKET_NAME"), "Key": name},
#                 ExpiresIn=3600,  # URL valable 1h
#             )
#         except Exception as e:
#             logger.warning(f"⚠️ URL signée B2 échouée pour {name}, fallback local: {e}")
#             return local_storage.url(name)

# # Alias pour compatibilité
# MediaStorage = FallbackMediaStorage

from storages.backends.s3boto3 import S3Boto3Storage

# ✅ Storage pour audio/vidéo (B2)
class MediaStorage(S3Boto3Storage):
    location = "media"
    default_acl = "private"          # fichiers protégés
    file_overwrite = False
    querystring_auth = True          # URLs signées temporaires
