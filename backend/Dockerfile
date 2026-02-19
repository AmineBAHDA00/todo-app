FROM python:3.11-slim

WORKDIR /app

# Dépendances Python avec versions spécifiées
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code de l'application
COPY . .

EXPOSE 5000

# Démarrage de l'application avec Gunicorn
# app.main:app -> module app/main.py, variable app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app.main:app"]

