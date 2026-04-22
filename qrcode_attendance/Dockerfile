# Utiliser une image Python officielle
FROM python:3.11-slim

# Définir des variables d'environnement
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir faker  # Assurer que faker est installé

# Copier le projet
COPY . /app/

# Donner les droits d'exécution à l'entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Exposer le port
EXPOSE 8080


# Utiliser l'entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
