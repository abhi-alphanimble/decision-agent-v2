"""
Main FastAPI application for Slack Decision Agent
"""
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
import logging
from typing import Optional
from slack_sdk.web import WebClient
import os
import asyncio
import httpx # Required for async http requests in process_command_async
import json
from datetime import datetime

# --- IMPORTS FOR SLACK CLIENT AND CONFIG ---
# Assuming these are available in your project structure
from app.slack_client import slack_client 
# from app.config import config # Assuming config is used by slack_client
# ------------------------------------------

# Assuming these are your database imports
from database.base import SessionLocal, engine, Base 

# Assuming these are your command-related imports
from app.command_parser import parse_message as parse_command
from app.handlers.decision_handlers import (
    handle_propose_command,
    handle_approve_command,
    handle_reject_command,
    handle_show_command,
    handle_myvote_command,
    handle_list_command,
    handle_help_command
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(title="Slack Decision Agent")

# Configuration (Replace with your actual values from the Slack App Management page)
CLIENT_ID = os.environ.get("SLACK_CLIENT_ID", "YOUR_SLACK_CLIENT_ID") 
CLIENT_SECRET = os.environ.get("SLACK_CLIENT_SECRET", "YOUR_SLACK_CLIENT_SECRET")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Slack Decision Agent is running",
        "version": "1.0.0"
    }


@app.post("/webhook/slack")
async def handle_slack_command(
    request: Request, # Added Request to access headers (though not strictly needed for commands)
    command: str = Form(...),
    text: str = Form(...),
    user_id: str = Form(...),
    user_name: str = Form(...),
    channel_id: str = Form(...),
    response_url: Optional[str] = Form(None),
    trigger_id: Optional[str] = Form(None)
):
    """
    Main endpoint for handling Slack slash commands.
    """
    logger.info(f"📨 Received command from {user_name} (ID: {user_id})")
    
    # ⚠️ NOTE: Slash commands don't *always* require signature verification 
    # if you use an immediate, ephemeral response, but it's good practice 
    # to perform it here if necessary for security.
    
    # Return immediate acknowledgment to Slack (prevent timeout)
    # Process command in background
    asyncio.create_task(
        process_command_async(
            text=text,
            user_id=user_id,
            user_name=user_name,
            channel_id=channel_id,
            response_url=response_url
        )
    )
    
    # Return immediate response
    return JSONResponse(content={
        "text": "⏳ Processing your command...",
        "response_type": "ephemeral"
    })


async def process_command_async(text, user_id, user_name, channel_id, response_url=None):
    """Process command asynchronously and send response via response_url or slack_client"""
    
    db = SessionLocal()
    
    try:
        # Parse the command
        parsed = parse_command(text)
        logger.info(f"📋 Parsed command: {parsed.command}")
        
        # Route to appropriate handler
        if parsed.command == "propose":
            response = handle_propose_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db
            )
        
        elif parsed.command == "approve":
            response = handle_approve_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db
            )
        
        elif parsed.command == "reject":
            response = handle_reject_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db
            )
        
        elif parsed.command == "show":
            response = handle_show_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db
            )
        
        elif parsed.command == "myvote":
            response = handle_myvote_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db
            )
        
        elif parsed.command == "list":
            response = handle_list_command(
                parsed=parsed,
                user_id=user_id,
                user_name=user_name,
                channel_id=channel_id,
                db=db
            )
        
        elif parsed.command == "help" or parsed.command == "":
            response = handle_help_command()
        
        else:
            response = {
                "text": f"❌ Unknown command: `{parsed.command}`\n\nUse `/decision help` to see available commands.",
                "response_type": "ephemeral"
            }
        
        # Send response
        if response_url:
            # Reply to Slash Command
            async with httpx.AsyncClient() as client:
                await client.post(response_url, json=response)
        else:
            # Reply to Event (Mention) via Slack Client
            if response.get("response_type") == "ephemeral":
                slack_client.send_ephemeral_message(
                    channel=channel_id,
                    user=user_id,
                    text=response.get("text", "")
                )
            else:
                slack_client.send_message(
                    channel=channel_id,
                    text=response.get("text", "")
                )
        
        logger.info(f"✅ Command processed: {parsed.command}")
    
    except Exception as e:
        logger.error(f"❌ Error processing command: {e}", exc_info=True)
        db.rollback()
        
        error_msg = f"❌ An internal error occurred: {str(e)}"
        
        if response_url:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(response_url, json={
                        "text": error_msg,
                        "response_type": "ephemeral"
                    })
            except:
                pass
        else:
            try:
                slack_client.send_ephemeral_message(
                    channel=channel_id,
                    user=user_id,
                    text=error_msg
                )
            except:
                pass
    
    finally:
        db.close()


def handle_list_command(parsed, user_id, user_name, channel_id, db):
    """
    Handle list command - shows all pending decisions.
    Command: /decision list
    """
    from app import crud
    
    logger.info(f"📋 Handling LIST from {user_name} in {channel_id}")
    
    # Get all pending decisions
    pending_decisions = crud.get_pending_decisions(db)
    
    if not pending_decisions:
        return {
            "text": "ℹ️ No pending decisions at the moment.\n\nCreate one with `/decision propose \"Your proposal\"`",
            "response_type": "ephemeral"
        }
    
    # Format list
    message = "📋 *Pending Decisions*\n\n"
    
    for decision in pending_decisions:
        message += f"*#{decision.id}* - {decision.text[:80]}{'...' if len(decision.text) > 80 else ''}\n"
        message += f"   👍 {decision.approval_count} approvals • 👎 {decision.rejection_count} rejections\n"
        message += f"   Proposed by: {decision.proposer_name}\n\n"
    
    message += f"\n*Commands:*\n"
    message += f"• `/decision show <id>` - View details\n"
    message += f"• `/decision approve <id>` - Vote to approve\n"
    message += f"• `/decision reject <id>` - Vote to reject\n"
    message += f"• Add `--anonymous` to any vote to keep it private"
    
    return {
        "text": message,
        "response_type": "ephemeral"
    }


def handle_help_command():
    """
    Handle help command - shows all available commands.
    Command: /decision help
    """
    logger.info("📖 Handling HELP command")
    
    help_text = """📚 *Slack Decision Agent - Command Reference*

*Creating Proposals:*
`/decision propose "Your proposal text"`
Create a new decision for the team to vote on.

*Voting Commands:*
`/decision approve <id>` - Vote to approve
`/decision reject <id>` - Vote to reject

*Anonymous Voting:*
`/decision approve <id> --anonymous` - Vote anonymously (long form)
`/decision approve <id> --anon` - Vote anonymously (short form)
`/decision approve <id> -a` - Vote anonymously (shortest form)

*Viewing Decisions:*
`/decision list` - Show all pending decisions
`/decision show <id>` - View decision details with votes
`/decision myvote <id>` - Check your vote on a decision

*Other Commands:*
`/decision help` - Show this help message

*Examples:*
• `/decision propose "Should we order pizza for lunch?"`
• `/decision approve 42`
• `/decision reject 42 --anonymous`
• `/decision show 42`
• `/decision myvote 42`

*Privacy Note:*
🔒 Anonymous votes hide your identity from other users, but you can always check your own vote using `/decision myvote <id>`.

*Questions?*
Contact your workspace admin for assistance.
"""
    
    return {
        "text": help_text,
        "response_type": "ephemeral"
    }


@app.post("/slack/events")
async def handle_slack_events(request: Request):
    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8")

    try:
        body = json.loads(body_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    # ✅ Handle URL verification FIRST — before signature check
    if body.get("type") == "url_verification":
        challenge = body.get("challenge")
        return JSONResponse(content={"challenge": challenge})

    # ✅ Only now verify signature for real events
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")

    if not slack_client.verify_slack_signature(body_str, timestamp, signature):
        raise HTTPException(status_code=403, detail="Signature verification failed")

    # Handle event_callback
    if body.get("type") == "event_callback":
        event = body.get("event", {})
        event_type = event.get("type")
        logger.info(f"Received event: {event.get('type')}")
        
        # Import helper to parse event
        from app.slack_utils import parse_event_message
        
        # We only care about messages or app_mentions
        if event_type in ["message", "app_mention"]:
            # Avoid processing bot's own messages
            if event.get("bot_id"):
                return JSONResponse(content={"status": "ignored_bot_message"})
                
            parsed_event = parse_event_message(event)
            
            if parsed_event and parsed_event.get("bot_mentioned"):
                text = parsed_event.get("text", "")
                user_id = parsed_event.get("user", "")
                channel_id = parsed_event.get("channel", "")
                
                # Extract command (remove mention)
                import re
                cleaned_text = re.sub(r'<@U[A-Z0-9]+>', '', text).strip()
                
                # Process in background
                asyncio.create_task(
                    process_command_async(
                        text=cleaned_text,
                        user_id=user_id,
                        user_name="User", # We don't have username in event
                        channel_id=channel_id,
                        response_url=None
                    )
                )

        return JSONResponse(content={"status": "ok"})

    return JSONResponse(content={"status": "ok"})


@app.get("/health")
async def health_check():
    """Detailed health check endpoint"""
    try:
        # Test database connection
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "ok",
        "database": db_status,
        "version": "1.0.0",
        "features": {
            "anonymous_voting": True,
            "vote_tracking": True,
            "decision_management": True
        }
    }


@app.get("/slack/install")
async def slack_install():
    """
    Initiates the Slack OAuth 2.0 installation flow.
    Redirects the user to Slack's authorization URL.
    """
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
        f"?client_id={CLIENT_ID}"
        f"&scope={','.join(scopes)}"
        f"&user_scope=" # Add user scopes if needed
    )
    
    return RedirectResponse(url=oauth_url)


@app.get("/slack/install/callback")
async def slack_callback(request: Request, code: Optional[str] = None):
    """
    Handles the Slack OAuth 2.0 redirect after a user approves the app installation.
    This is the Redirect URL.
    """
    if not code:
        # User denied installation
        error = request.query_params.get("error", "No code received")
        logger.error(f"❌ OAuth failed: {error}")
        return JSONResponse(
            content={"message": f"Installation failed. Reason: {error}"},
            status_code=400
        )

    # Initialize DB Session
    db = SessionLocal()

    try:
        # 1. Exchange the temporary code for permanent tokens
        client = WebClient()
        oauth_response = client.oauth_v2_access(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            code=code,
        )
        
        # 2. Extract and store the necessary tokens/IDs
        team_id = oauth_response["team"]["id"]
        team_name = oauth_response["team"]["name"]
        bot_token = oauth_response["access_token"]
        bot_user_id = oauth_response["bot_user_id"]
        
        # --- CRITICAL: PERSISTENCE STEP ---
        # You MUST save 'bot_token' and 'team_id' to your database here.
        # This token is what you will use to send messages to this new workspace.
        logger.info(f"🔑 Successfully installed in Team ID: {team_id} ({team_name})")
        logger.info(f"💾 Storing new bot token for workspace {team_id}")

        # Import the model here to avoid circular imports if any
        from app.models import SlackInstallation
        
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
    finally:
        # 4. Ensure DB session is closed
        db.close()


def main():
    """
    Entry point for running the application.
    """
    import uvicorn
    
    print("🚀 Starting Slack Decision Agent...")
    print("📊 Features enabled:")
    print("   ✅ Decision proposals")
    print("   ✅ Anonymous voting (--anonymous, --anon, -a)")
    print("   ✅ Vote tracking")
    print("   ✅ Decision management")
    print("\n🌐 Server will start on http://0.0.0.0:8000")
    print("📡 Slack commands endpoint: http://0.0.0.0:8000/webhook/slack")
    print("📡 Slack events endpoint: http://0.0.0.0:8000/slack/events")
    print("📡 Slack install endpoint: http://0.0.0.0:8000/slack/install")
    print("\n💡 Use Ctrl+C to stop the server\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )


if __name__ == "__main__":
    main()