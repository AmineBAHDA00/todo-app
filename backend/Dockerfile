FROM python:3.9-slim
WORKDIR /app
# On copie le fichier que tu as créé manuellement
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]