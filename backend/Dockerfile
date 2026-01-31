FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Cloud Run will provide $PORT, usually 8080.
# We must listen on 0.0.0.0 to receive external requests.
CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"
