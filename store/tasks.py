import os
import tempfile
import logging
from pathlib import Path

from celery import shared_task
from django.conf import settings
from django.core.files import File

from .models import MediaFile
from .media_converter import process_media

logger = logging.getLogger(__name__)

# =========================
# CLIENT B2 (via boto3 déjà dans media_converter)
# =========================

def download_to_tmp(media):
    """
    Télécharge le fichier depuis B2 vers un fichier temporaire et retourne le chemin local.
    """
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    try:
        # Le client S3 est déjà géré dans media_converter.py
        from .media_converter import s3
        s3.download_fileobj(settings.AWS_STORAGE_BUCKET_NAME, media.file.name, tmp_file)
        tmp_file.flush()
        return tmp_file.name
    except Exception as e:
        logger.error(f"❌ Impossible de télécharger {media.file.name}: {e}")
        tmp_file.close()
        os.unlink(tmp_file.name)
        raise

# =========================
# TÂCHE CELERY
# =========================
@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={"max_retries": 3})
def convert_media_task(self, media_id):
    local_path = None
    media = None

    try:
        media = MediaFile.objects.get(id=media_id)
        media.conversion_status = "processing"
        media.save(update_fields=["conversion_status"])

        logger.info(f"🎬 Conversion en cours pour MediaFile {media.id}")

        # ✅ Télécharger le fichier depuis B2
        local_path = download_to_tmp(media)

        # ✅ Pipeline média (conversion + upload direct sur B2)
        results = process_media(local_path, remote_prefix=f"media/{media.id}/")

        # === AUDIO ===
        if results.get("opus"):
            media.opus_file.name = results["opus"]
        if results.get("aac"):
            media.aac_file.name = results["aac"]

        # === VIDEO ===
        if results.get("mp4"):
            media.mp4_file.name = results["mp4"]

        # === THUMBNAILS ===
        if results.get("thumbs") and len(results["thumbs"]) > 0:
            media.thumbnail.name = results["thumbs"][0]

        media.conversion_status = "done"
        media.save()
        logger.info(f"✅ Conversion terminée pour MediaFile {media.id}")

    except MediaFile.DoesNotExist:
        logger.error(f"❌ MediaFile {media_id} introuvable")
    except Exception as e:
        logger.error(f"❌ Erreur conversion MediaFile {media_id}: {e}")
        if media:
            media.conversion_status = "failed"
            media.save(update_fields=["conversion_status"])
        raise
    finally:
        # ✅ Nettoyage du fichier temporaire
        if local_path and os.path.exists(local_path):
            os.remove(local_path)
            logger.info(f"🧹 Fichier temporaire supprimé : {local_path}")
