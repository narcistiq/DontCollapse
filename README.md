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