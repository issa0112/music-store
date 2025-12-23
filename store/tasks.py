# store/tasks.py
import os
import logging
from celery import shared_task
from django.core.files import File
from .models import MediaFile
from media_converter import process_media

logger = logging.getLogger(__name__)

@shared_task
def convert_media_task(media_id):
    try:
        instance = MediaFile.objects.get(id=media_id)
    except MediaFile.DoesNotExist:
        logger.error(f"❌ MediaFile {media_id} introuvable")
        return "Fichier non trouvé"

    try:
        logger.info(f"🚀 Conversion démarrée pour {instance.title} ({instance.id})")
        results = process_media(instance.file.path)

        if results.get("opus"):
            with open(results["opus"], "rb") as f:
                instance.opus_file.save(os.path.basename(results["opus"]), File(f), save=False)

        if results.get("aac"):
            with open(results["aac"], "rb") as f:
                instance.aac_file.save(os.path.basename(results["aac"]), File(f), save=False)

        if results.get("mp4"):
            with open(results["mp4"], "rb") as f:
                instance.mp4_file.save(os.path.basename(results["mp4"]), File(f), save=False)

        if results.get("webm"):
            with open(results["webm"], "rb") as f:
                instance.webm_file.save(os.path.basename(results["webm"]), File(f), save=False)

        if results.get("thumbs"):
            with open(results["thumbs"][0], "rb") as f:
                instance.thumbnail.save(os.path.basename(results["thumbs"][0]), File(f), save=False)

        instance.conversion_status = "success"
        instance.save()
        logger.info(f"✅ Conversion terminée pour {instance.title} ({instance.id})")
        return "Conversion terminée"

    except Exception as e:
        instance.conversion_status = "failed"
        instance.save()
        logger.error(f"❌ Erreur conversion {instance.id}: {e}")
        return f"Erreur conversion: {e}"
