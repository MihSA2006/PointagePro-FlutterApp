#!/bin/bash

echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Appliquer les migrations
echo "Appliquer les migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "Collecter les fichiers statiques..."
python manage.py collectstatic --noinput

# Exécuter le script de seeding
echo "Exécution du script de seeding..."
python seed_all_data.py

# Démarrer le serveur
echo "Démarrer le serveur sur le port 8080..."
python manage.py runserver 0.0.0.0:8080

