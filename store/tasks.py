from celery import shared_task
from django.core.files import File
from pathlib import Path
import logging

from .models import MediaFile
from .media_converter import process_media

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=10, retry_kwargs={"max_retries": 3})
def convert_media_task(self, media_id):
    try:
        media = MediaFile.objects.get(id=media_id)

        media.conversion_status = "processing"
        media.save(update_fields=["conversion_status"])

        logger.info(f"🎬 Conversion en cours pour MediaFile {media.id}")

        # Vérification du fichier
        if not media.file or not Path(media.file.path).exists():
            logger.error(f"❌ Fichier introuvable pour MediaFile {media.id}")
            media.conversion_status = "failed"
            media.save(update_fields=["conversion_status"])
            return

        # Pipeline média
        results = process_media(media.file.path)

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
        # Pas de retry inutile
    except Exception as e:
        logger.error(f"❌ Erreur conversion MediaFile {media_id}: {e}")
        try:
            media = MediaFile.objects.get(id=media_id)
            media.conversion_status = "failed"
            media.save(update_fields=["conversion_status"])
        except Exception:
            pass
        raise
