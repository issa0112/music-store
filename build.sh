#!/usr/bin/env bash

# Arrêter le script si une commande échoue
set -o errexit

# Installer les dépendances
pip install -r requirements.txt

# Appliquer les migrations
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
