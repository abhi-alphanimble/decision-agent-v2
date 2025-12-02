# API Endpoints

This project is a FastAPI app exposing several HTTP endpoints used by Slack and for health/status checks.

Key endpoints (all under `/` unless otherwise noted):

- `POST /slack/commands` — Slack slash command receiver. Handles `/decision` commands.
- `POST /slack/events` — Slack Event API endpoint for event callbacks.
- `GET /health` — Health check endpoint returning `200 OK` and a JSON status object.
- `GET /status` — Application status including database and AI status.

All Slack endpoints expect Slack-style verification (signing secret).
