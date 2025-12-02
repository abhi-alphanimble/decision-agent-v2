@echo off
echo Starting Slack Decision Agent API...
echo.
echo Make sure your .env file is configured with:
echo   - SLACK_CLIENT_ID
echo   - SLACK_CLIENT_SECRET  
echo   - SLACK_BOT_TOKEN
echo   - SLACK_SIGNING_SECRET
echo.
echo Server will start on http://0.0.0.0:8000
echo Press CTRL+C to stop
echo.

python run.py
