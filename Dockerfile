FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Augmenter le délai de téléchargement (300 secondes = 5 minutes)
ENV PIP_DEFAULT_TIMEOUT=300

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
