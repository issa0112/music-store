# store/signals.py
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MediaFile
from .tasks import convert_media_task

logger = logging.getLogger(__name__)

@receiver(post_save, sender=MediaFile)
def trigger_media_conversion(sender, instance, created, **kwargs):
    if created and instance.file:
        logger.info(f"📥 Upload détecté pour {instance.title} ({instance.id}), lancement conversion…")
        # Mettre le statut en pending sans relancer le signal
        MediaFile.objects.filter(id=instance.id).update(conversion_status="pending")
        # Lancer la tâche Celery dans une queue dédiée
        convert_media_task.apply_async(args=[instance.id], queue="media")
