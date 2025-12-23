#!/usr/bin/env bash
set -o errexit

# Mettre à jour pip et outils de build
pip install --upgrade pip setuptools wheel

# Installer FFmpeg et autres dépendances système
apt-get update && apt-get install -y ffmpeg

# Installer les dépendances Python
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate --noinput
python manage.py migrate django_celery_results --noinput
python manage.py migrate django_celery_beat --noinput

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
