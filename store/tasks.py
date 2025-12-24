import boto3, tempfile, os
from django.conf import settings
from celery import shared_task
from django.core.files import File
from pathlib import Path
import logging

from .models import MediaFile
from .media_converter import process_media

logger = logging.getLogger(__name__)

# Client S3 (Backblaze B2 via django-storages)
s3 = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
)

def download_to_tmp(media):
    """Télécharge le fichier depuis B2 vers /tmp et retourne le chemin local"""
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    s3.download_fileobj(settings.AWS_STORAGE_BUCKET_NAME, media.file.name, tmp_file)
    tmp_file.flush()
    return tmp_file.name

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={"max_retries": 3})
def convert_media_task(self, media_id):
    local_path = None
    try:
        media = MediaFile.objects.get(id=media_id)
        media.conversion_status = "processing"
        media.save(update_fields=["conversion_status"])

        logger.info(f"🎬 Conversion en cours pour MediaFile {media.id}")

        # ✅ Télécharger le fichier depuis B2
        local_path = download_to_tmp(media)

        # Pipeline média
        results = process_media(local_path)

        # === AUDIO ===
        if results.get("opus"):
            with open(results["opus"], "rb") as f:
                media.opus_file.save(Path(results["opus"]).name, File(f), save=True)

        if results.get("aac"):
            with open(results["aac"], "rb") as f:
                media.aac_file.save(Path(results["aac"]).name, File(f), save=True)

        # === VIDEO ===
        if results.get("mp4"):
            with open(results["mp4"], "rb") as f:
                media.mp4_file.save(Path(results["mp4"]).name, File(f), save=True)

        # === THUMBNAIL ===
        if results.get("thumbs"):
            with open(results["thumbs"][0], "rb") as f:
                media.thumbnail.save(Path(results["thumbs"][0]).name, File(f), save=True)

        media.conversion_status = "done"
        media.save()
        logger.info(f"✅ Conversion terminée pour MediaFile {media.id}")

    except FileNotFoundError as e:
        logger.error(f"❌ Fichier manquant pour MediaFile {media_id}: {e}")
        media = MediaFile.objects.get(id=media_id)
        media.conversion_status = "failed"
        media.save(update_fields=["conversion_status"])
    except Exception as e:
        logger.error(f"❌ Erreur conversion MediaFile {media_id}: {e}")
        try:
            media = MediaFile.objects.get(id=media_id)
            media.conversion_status = "failed"
            media.save(update_fields=["conversion_status"])
        except Exception:
            pass
        raise
    finally:
        # ✅ Nettoyage du fichier temporaire
        if local_path and os.path.exists(local_path):
            os.remove(local_path)
            logger.info(f"🧹 Fichier temporaire supprimé : {local_path}")
