# Deploying Simulation Server to Google Cloud

This guide provides step-by-step instructions to deploy the `SimulationServer` backend to Google Cloud Run.

## Prerequisites

1.  **Google Cloud Project**: You need a Google Cloud project with billing enabled.
2.  **gcloud CLI**: Ensure the Google Cloud CLI is installed.

## Step 1: Initialize gcloud

If you haven't already, log in and set your project:

```sh
# Login to Google Cloud
gcloud auth login

# List your projects to find the PROJECT_ID
gcloud projects list

# Set the active project (replace YOUR_PROJECT_ID)
gcloud config set project YOUR_PROJECT_ID
```

## Step 2: Enable Required Services

Enable the Cloud Run and Container Registry/Artifact Registry APIs:

```sh
gcloud services enable run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com
```

## Step 3: Deploy to Cloud Run

We can use the `gcloud run deploy` command, which handles building the container (using Google Cloud Build) and deploying it in one step.

Run this command from the `backend` directory (where the `Dockerfile` is):

```sh
cd backend

gcloud run deploy simulation-server \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_URL="https://example.com/api/agent"
```

*   **`simulation-server`**: The name of your Cloud Run service.
*   **`--source .`**: Builds the container from the current directory.
*   **`--region us-central1`**: You can choose a different region (e.g., `europe-west1`).
*   **`--allow-unauthenticated`**: Makes the server publicly accessible. **Remove this if you want it private.**
*   **`--set-env-vars`**: Sets environment variables. Replace `https://example.com/api/agent` with the URL of your actual AI agent if you have one.

## Step 4: Verify Deployment

1.  `gcloud` will output a **Service URL** (e.g., `https://simulation-server-xyz-uc.a.run.app`).
2.  Open that URL in your browser. You should see `{"message": "Incident Response Simulation Backend"}`.
3.  Test metrics: `YOUR_URL/metrics`.

## Troubleshooting

-   **Deployment fails**: Check the logs using the link provided in the terminal.
-   **Service unavailable**: Ensure the `Dockerfile` is listening on the port provided by the `PORT` environment variable (we updated this in the code).

## Simulating Incidents

Once deployed, you can trigger incidents using `curl`:

```sh
# Trigger Memory Leak
curl -X POST YOUR_SERVICE_URL/simulate/memory_leak

# Trigger Disk Full
curl -X POST YOUR_SERVICE_URL/simulate/disk_full
```
