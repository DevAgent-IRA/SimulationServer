# Deploying Simulation Server to Google Cloud

This guide provides step-by-step instructions to deploy the `SimulationServer` backend to Google Cloud Run.

## Prerequisites

1.  **Google Cloud Project**: You need a Google Cloud project with billing enabled.
2.  **gcloud CLI**: Ensure the Google Cloud CLI is installed.

---

## Option 1: Automated Deployment with GitHub Actions (Recommended)

This project includes a GitHub Actions workflow that automatically deploys to Cloud Run on every push to the `main` branch.

### Step 1: Enable Required GCP Services

```sh
gcloud services enable run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    iam.googleapis.com
```

### Step 2: Create Artifact Registry Repository

Create a repository to store Docker images:

```sh
gcloud artifacts repositories create cloud-run-source-deploy \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker images for Cloud Run deployments"
```

### Step 3: Create a Service Account for GitHub Actions

```sh
# Create service account
gcloud iam service-accounts create github-deployer \
    --display-name="GitHub Actions Cloud Run Deployer"

# Get your project ID
PROJECT_ID=$(gcloud config get-value project)

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:github-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/iam.serviceAccountUser"

# Create and download the key
gcloud iam service-accounts keys create key.json \
    --iam-account=github-deployer@$PROJECT_ID.iam.gserviceaccount.com
```

### Step 4: Configure GitHub Secrets

Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** and add:

| Secret Name | Description | How to Get |
|-------------|-------------|------------|
| `GCP_PROJECT_ID` | Your Google Cloud project ID | `gcloud config get-value project` |
| `GCP_SA_KEY` | Service account JSON key | Contents of `key.json` file created above |
| `AGENT_URL` | URL of your AI agent | Your agent's URL (optional) |

> ⚠️ **Security Note**: After adding `key.json` to GitHub Secrets, delete it from your local machine:
> ```sh
> rm key.json
> ```

### Step 5: Deploy

The workflow triggers automatically on:
- Push to `main` branch
- Manual trigger from GitHub Actions tab

To manually trigger:
1. Go to your repository → **Actions**
2. Select **"Deploy to Cloud Run"**
3. Click **"Run workflow"**

### Verify Deployment

After the workflow completes:
1. Check the workflow logs for the Service URL
2. Or run: `gcloud run services describe simulation-server --region us-central1 --format 'value(status.url)'`

---

## Option 2: Manual Deployment

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
