import logging
from storages.backends.s3boto3 import S3Boto3Storage

logger = logging.getLogger(__name__)

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
