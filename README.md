# DontCollapse

Initial repository baseline for a multi-branch build-out.

## Bootstrap

This repo currently includes only foundational setup:

- `.gitignore` for common local/build artifacts
- `.env.example` for environment variable placeholders
- `.editorconfig` for consistent formatting defaults
- `.gitattributes` for LF line ending normalization

## Branching

Use `test` as the integration base for upcoming workstreams (frontend, data, and AI/backend).

## Stitch Setup (Frontend)

Configured for:

- Project: Main Dashboard (`8905614730279918180`)
- Screen: Main Dashboard (`4f6dfb5ac2f04f3da9be4680840e9b99`)

Files:

- `stitch/stitch.config.sh` holds Stitch IDs and hosted URLs.
- `scripts/fetch-stitch.sh` downloads image and code artifacts with `curl -L`.

Usage:

1. Add hosted URLs to `SCREEN_IMAGE_URL` and `SCREEN_CODE_URL` in `stitch/stitch.config.sh`.
2. Run:

```bash
chmod +x scripts/fetch-stitch.sh
./scripts/fetch-stitch.sh
```

Downloads are written to `stitch/downloads/<SCREEN_ID>/`.

## Frontend Dashboard (Next.js)

This repo now includes a single-page frontend implementation for the Tampa Bay Resilience Ecosystem dashboard using:

- Next.js (App Router)
- Tailwind CSS
- Mapbox GL JS
- lucide-react

Run locally:

```bash
npm install
cp .env.example .env.local
# set NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN in .env.local
npm run dev
```

Quality checks:

```bash
npm run lint
npm run build
```

## Google Cloud Deployment (dontcollapse.tech)

This repo includes scripts to enable required Google Cloud APIs and deploy to Cloud Run.

Files:

- `scripts/setup-gcp.sh` enables required APIs and prepares Artifact Registry.
- `scripts/deploy-gcp.sh` builds and deploys the app to Cloud Run.
- `Dockerfile` builds a production Next.js standalone container.

Run once (API and registry setup):

```bash
chmod +x scripts/setup-gcp.sh scripts/deploy-gcp.sh
./scripts/setup-gcp.sh <PROJECT_ID> us-central1 dontcollapse.tech dontcollapse-web dontcollapse
```

Deploy:

```bash
export NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN=<your_mapbox_token>
./scripts/deploy-gcp.sh <PROJECT_ID> us-central1 dontcollapse-web dontcollapse
```

Map custom domain:

```bash
gcloud beta run domain-mappings create \
	--service dontcollapse-web \
	--domain dontcollapse.tech \
	--region us-central1

gcloud beta run domain-mappings describe \
	--domain dontcollapse.tech \
	--region us-central1
```

Add the returned DNS records at your domain registrar for `dontcollapse.tech`.