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
        # Récupération du media
        media = MediaFile.objects.get(id=media_id)

        media.conversion_status = "processing"
        media.save(update_fields=["conversion_status"])

        logger.info(f"🎬 Conversion en cours pour MediaFile {media.id}")

        # Pipeline média (audio / vidéo / thumbs)
        results = process_media(media.file.path)

        # === AUDIO ===
        if results.get("opus"):
            with open(results["opus"], "rb") as f:
                media.opus_file.save(Path(results["opus"]).name, File(f), save=False)

        if results.get("aac"):
            with open(results["aac"], "rb") as f:
                media.aac_file.save(Path(results["aac"]).name, File(f), save=False)

        # === VIDEO ===
        if results.get("mp4"):
            with open(results["mp4"], "rb") as f:
                media.mp4_file.save(Path(results["mp4"]).name, File(f), save=False)

        # === THUMBNAIL ===
        if results.get("thumbs"):
            with open(results["thumbs"][0], "rb") as f:
                media.thumbnail.save(Path(results["thumbs"][0]).name, File(f), save=False)

        # Mise à jour du statut final
        media.conversion_status = "done"
        media.save()

        logger.info(f"✅ Conversion terminée pour MediaFile {media.id}")

    except Exception as e:
        # Log de l'erreur
        logger.error(f"❌ Erreur conversion MediaFile {media_id}: {e}")

        # Essai de mettre le statut "failed" si possible
        try:
            media = MediaFile.objects.get(id=media_id)
            media.conversion_status = "failed"
            media.save(update_fields=["conversion_status"])
        except Exception:
            pass

        # Remonte l’exception pour que Celery puisse relancer la tâche
        raise
