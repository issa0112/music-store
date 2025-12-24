import os
import ssl
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "music_store.settings")

app = Celery("music_store")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# 🔐 Configuration SSL pour Redis (Upstash rediss://)
app.conf.broker_use_ssl = {
    "ssl_cert_reqs": ssl.CERT_NONE  # ✅ évite les warnings, connexion TLS reste active
}
