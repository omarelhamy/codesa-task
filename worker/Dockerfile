FROM python:3.9-slim

WORKDIR /app

COPY worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY models.py .
COPY worker/ .

CMD ["python", "worker.py"]
