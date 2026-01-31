# Incident Response Simulation Backend

This project simulates various system incidents (Memory Leak, API Timeout, Disk Full) and logs them in JSON format. It is designed to be a telemetry source for an Intelligent Incident Response Agent.

## Setup

### 1. Build Docker Image
```bash
cd backend
docker build -t incident-backend .
```

### 2. Run Container
```bash
docker run -p 8000:8000 incident-backend
```

## triggers

### Memory Leak
Simulates a gradual memory leak.
```bash
curl -X POST http://localhost:8000/simulate/memory_leak
```

### API Timeout
Simulates an endpoint that hangs for 30 seconds.
```bash
curl -X POST "http://localhost:8000/simulate/timeout?duration=5"
```

### Disk Full
Simulates a disk full scenario (logs and metrics).
```bash
curl -X POST http://localhost:8000/simulate/disk_full
```

## Logs
The application outputs logs in JSON format to stdout. When running in Docker, you can view them with:
```bash
docker logs <container_id>
```


## Deployment on Google Cloud Run

1. **Authenticate & Set Project**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Build & Push Container**:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/incident-backend
   ```

3. **Deploy**:
   ```bash
   gcloud run deploy incident-backend --image gcr.io/YOUR_PROJECT_ID/incident-backend --platform managed --region us-central1 --allow-unauthenticated
   ```

4. **Accessing Logs**:
   - Google Cloud Run automatically captures `stdout` logs.
   - Go to **Cloud Logging** in the GCP Console.
   - The logs will appear in structured JSON format, ready for your AI Agent to query via the Cloud Logging API.
   - *Note: The local `backend_logs.json` file is ephemeral in Cloud Run (lost on restart), so rely on Cloud Logging (stdout) for production.*

## Agent Notification
The application tries to send a POST request to a configured agent URL.
 Currently it defaults to just logging the attempt if no URL is provided (which is the default).
