# Setup & Deployment Notes

This document outlines steps to prepare and run Decision Agent locally and tips for production deployment.

## Local Setup

1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

2. Install dependencies

```powershell
pip install -r requirements.txt
```

3. Configure environment variables

Create a `.env` file in project root with values for:
- `DATABASE_URL` (e.g., `sqlite:///./dev.db`) or leave unset to use SQLite memory in tests
- `SLACK_BOT_TOKEN`
- `SLACK_SIGNING_SECRET`
- `GEMINI_API_KEY` (optional for AI features)

4. Initialize database (alembic):

```powershell
alembic upgrade head
```

5. Start the app locally

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Production Tips

- Use a robust Postgres or MySQL database instead of SQLite.
- Run the app under an ASGI server such as `uvicorn` or `gunicorn` with multiple workers behind a reverse proxy (nginx).
- Supply secrets via your platform's secret manager or environment variables.
- Add monitoring and log rotation for production logs.

## Docker (optional)

Create a Dockerfile and a `docker-compose.yml` to bundle the app with a database.

## CI/CD

- Run `pytest` in CI with `TESTING=1` to ensure tests run with mocks.
