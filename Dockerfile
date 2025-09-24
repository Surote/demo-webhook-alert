FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY alertmanager_webhook.py .

EXPOSE 8080

CMD ["python", "alertmanager_webhook.py"]