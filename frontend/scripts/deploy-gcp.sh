#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:-}"
REGION="${2:-us-central1}"
SERVICE="${3:-dontcollapse-web}"
REPO="${4:-dontcollapse}"
TAG="${5:-$(date +%Y%m%d-%H%M%S)}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}:${TAG}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Usage: scripts/deploy-gcp.sh <PROJECT_ID> [REGION] [SERVICE] [REPO] [TAG]" >&2
  exit 1
fi

echo "Building image: $IMAGE"
gcloud builds submit --tag "$IMAGE"

DEPLOY_ARGS=(
  run deploy "$SERVICE"
  --image "$IMAGE"
  --platform managed
  --region "$REGION"
  --allow-unauthenticated
  --port 8080
)

if [[ -n "${NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN:-}" ]]; then
  DEPLOY_ARGS+=(--set-env-vars "NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN=${NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN}")
fi

echo "Deploying Cloud Run service: $SERVICE"
gcloud "${DEPLOY_ARGS[@]}"

echo
echo "Deployment complete. Service URL:"
gcloud run services describe "$SERVICE" --region "$REGION" --format='value(status.url)'
