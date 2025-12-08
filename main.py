"""
Main entry point for Slack Decision Agent.

This file serves as the single entry point for the application.
All application logic is in the `app` package.
"""
import os

# Import the FastAPI app from the app package
from app.main import app

# Re-export for uvicorn and other tools
__all__ = ["app"]


def main():
    """
    Entry point for running the application.
    Use this for development: python main.py
    For production, use: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
    """
    import uvicorn  # Import here to avoid requiring it for simple imports
    
    # Only configure environment-specific settings here
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    reload = os.getenv("ENV", "development") == "development"
    
    print(f"🚀 Starting Slack Decision Agent on http://{host}:{port}")
    print(f"📡 Slack webhook endpoint: http://{host}:{port}/webhook/slack")
    print(f"📡 Slack events endpoint: http://{host}:{port}/slack/events")
    print(f"📚 API docs: http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()