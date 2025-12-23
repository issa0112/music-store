#!/usr/bin/env bash
set -o errexit

# Installer FFmpeg et autres dépendances système
apt-get update && apt-get install -y ffmpeg

# Installer les dépendances Python
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
