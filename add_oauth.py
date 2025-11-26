#!/usr/bin/env python3
"""Script to add OAuth endpoints to app/main.py"""

oauth_code = '''

# Slack OAuth installation endpoints
@app.get("/slack/install")
async def slack_install():
    """
    Initiates the Slack OAuth 2.0 installation flow.
    Redirects the user to Slack's authorization URL.
    """
    from app.config import config
    from fastapi.responses import RedirectResponse
    
    # Scopes required for the bot
    scopes = [
        "chat:write",
        "commands",
        "app_mentions:read",
        "channels:history",
        "groups:history",
        "im:history",
        "mpim:history"
    ]
    
    # Build the OAuth URL
    oauth_url = (
        f"https://slack.com/oauth/v2/authorize"
        f"?client_id={config.SLACK_CLIENT_ID}"
        f"&scope={','.join(scopes)}"
        f"&user_scope="  # Add user scopes if needed
    )
    
    return RedirectResponse(url=oauth_url)


@app.get("/slack/install/callback")
async def slack_callback(request: Request, code: str = None, db: Session = Depends(get_db)):
    """
    Handles the Slack OAuth 2.0 redirect after a user approves the app installation.
    This is the Redirect URL.
    """
    from app.config import config
    from slack_sdk.web import WebClient
    from app.models import SlackInstallation
    from fastapi.responses import RedirectResponse
    
    if not code:
        # User denied installation
        error = request.query_params.get("error", "No code received")
        logger.error(f"❌ OAuth failed: {error}")
        return JSONResponse(
            content={"message": f"Installation failed. Reason: {error}"},
            status_code=400
        )

    try:
        # 1. Exchange the temporary code for permanent tokens
        client = WebClient()
        oauth_response = client.oauth_v2_access(
            client_id=config.SLACK_CLIENT_ID,
            client_secret=config.SLACK_CLIENT_SECRET,
            code=code,
        )
        
        # 2. Extract and store the necessary tokens/IDs
        team_id = oauth_response["team"]["id"]
        team_name = oauth_response["team"]["name"]
        bot_token = oauth_response["access_token"]
        bot_user_id = oauth_response["bot_user_id"]
        
        # --- CRITICAL: PERSISTENCE STEP ---
        # Save bot_token and team_id to database
        logger.info(f"🔑 Successfully installed in Team ID: {team_id} ({team_name})")
        logger.info(f"💾 Storing new bot token for workspace {team_id}")
        
        # Check if installation already exists
        installation = db.query(SlackInstallation).filter(SlackInstallation.team_id == team_id).first()
        
        if installation:
            # Update existing installation
            installation.access_token = bot_token
            installation.bot_user_id = bot_user_id
            installation.team_name = team_name
            installation.installed_at = datetime.utcnow()
            logger.info(f"🔄 Updated existing installation for {team_name}")
        else:
            # Create new installation
            installation = SlackInstallation(
                team_id=team_id,
                team_name=team_name,
                access_token=bot_token,
                bot_user_id=bot_user_id
            )
            db.add(installation)
            logger.info(f"✨ Created new installation for {team_name}")
            
        db.commit()
        
        # 3. Final Redirect to the new workspace in Slack
        return RedirectResponse(url=f"slack://app?team={team_id}")

    except Exception as e:
        logger.error(f"❌ OAuth Access Error: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail="Failed to complete app installation."
        )
'''

# Read the current main.py
with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Append the OAuth code
with open('app/main.py', 'a', encoding='utf-8') as f:
    f.write(oauth_code)

print("✅ OAuth endpoints added to app/main.py")
