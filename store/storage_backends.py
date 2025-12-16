import logging
from django.conf import settings

logger = logging.getLogger(__name__)

if not settings.DEBUG:
    from storages.backends.s3boto3 import S3Boto3Storage

    class MediaStorage(S3Boto3Storage):
        location = 'media'          # dossier virtuel dans le bucket
        file_overwrite = False

        def _save(self, name, content):
            try:
                result = super()._save(name, content)
                logger.info(f"Successfully uploaded {name} to Backblaze B2")
                return result
            except Exception as e:
                logger.error(f"Failed to upload {name} to Backblaze B2: {str(e)}")
                raise
else:
    # DEBUG / local : ne fait rien
    MediaStorage = None
