# Image Python
FROM python:3.11-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED=1

# Créer le répertoire de travail
WORKDIR /app

# Copier requirements
COPY requirements.txt .

# Installer dépendances
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code
COPY . .

# Commande par défaut pour lancer le scraping + sauvegarde
CMD ["python", "main.py"]
