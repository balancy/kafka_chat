FROM python:3.11-slim

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x wait_for_kafka.sh

CMD ["./wait_for_kafka.sh", "kafka", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
