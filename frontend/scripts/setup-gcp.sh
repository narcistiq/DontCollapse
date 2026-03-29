#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:-}"
REGION="${2:-us-central1}"
DOMAIN="${3:-dontcollapse.tech}"
SERVICE="${4:-dontcollapse-web}"
REPO="${5:-dontcollapse}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Usage: scripts/setup-gcp.sh <PROJECT_ID> [REGION] [DOMAIN] [SERVICE] [REPO]" >&2
  exit 1
fi

echo "Setting gcloud project to $PROJECT_ID"
gcloud config set project "$PROJECT_ID"

echo "Enabling required Google Cloud APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  domains.googleapis.com \
  certificatemanager.googleapis.com

echo "Ensuring Artifact Registry repo exists: $REPO"
if ! gcloud artifacts repositories describe "$REPO" --location "$REGION" >/dev/null 2>&1; then
  gcloud artifacts repositories create "$REPO" \
    --repository-format=docker \
    --location="$REGION" \
    --description="DontCollapse container images"
fi

echo
echo "Initial setup complete."
echo "Next steps:"
echo "1) Deploy: scripts/deploy-gcp.sh $PROJECT_ID $REGION $SERVICE $REPO"
echo "2) Map domain:" 
echo "   gcloud beta run domain-mappings create --service $SERVICE --domain $DOMAIN --region $REGION"
echo "3) Get DNS records to add at your registrar:" 
echo "   gcloud beta run domain-mappings describe --domain $DOMAIN --region $REGION"
