"""
Main FastAPI application for Slack Decision Agent
"""
from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
from typing import Optional

from app.database import SessionLocal, engine, Base
from app.command_parser import parse_command
from app.handlers import (
    handle_propose_command,
    handle_approve_command,
    handle_reject_command,
    handle_show_command,
    handle_myvote_command
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


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Slack Decision Agent is running",
        "version": "1.0.0"
    }


@app.post("/slack/commands")
async def handle_slack_command(
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
    
    Supports:
    - /decision propose "text"
    - /decision approve <id> [--anonymous|--anon|-a]
    - /decision reject <id> [--anonymous|--anon|-a]
    - /decision show <id>
    - /decision myvote <id>
    - /decision list
    """
    logger.info(f"📨 Received command from {user_name} (ID: {user_id})")
    logger.info(f"   Command: {command}")
    logger.info(f"   Text: {text}")
    logger.info(f"   Channel: {channel_id}")
    
    # Return immediate acknowledgment to Slack (prevent timeout)
    import asyncio
    from fastapi import BackgroundTasks
    
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


async def process_command_async(text, user_id, user_name, channel_id, response_url):
    """Process command asynchronously and send response via response_url"""
    import httpx
    
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
        
        # Send response via response_url
        if response_url:
            async with httpx.AsyncClient() as client:
                await client.post(response_url, json=response)
        
        logger.info(f"✅ Command processed: {parsed.command}")
    
    except Exception as e:
        logger.error(f"❌ Error processing command: {e}", exc_info=True)
        db.rollback()
        
        # Send error via response_url
        if response_url:
            try:
                async with httpx.AsyncClient() as client:
                    await client.post(response_url, json={
                        "text": f"❌ An error occurred: {str(e)}",
                        "response_type": "ephemeral"
                    })
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
        message += f"   👍 {decision.approval_count} approvals • 👎 {decision.rejection_count} rejections\n"
        message += f"   Proposed by: {decision.proposer_name}\n\n"
    
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
    """
    Handle Slack Events API callbacks.
    Used for URL verification and future event subscriptions.
    """
    try:
        body = await request.json()
        
        # Handle URL verification challenge
        if body.get("type") == "url_verification":
            logger.info("🔐 Handling Slack URL verification")
            return JSONResponse(content={"challenge": body.get("challenge")})
        
        # Handle other events (future implementation)
        if body.get("type") == "event_callback":
            event = body.get("event", {})
            logger.info(f"📨 Received event: {event.get('type')}")
            # TODO: Handle events as needed
        
        return JSONResponse(content={"status": "ok"})
    
    except Exception as e:
        logger.error(f"❌ Error handling event: {e}", exc_info=True)
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )


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


def main():
    """
    Entry point for running the application.
    """
    import uvicorn
    
    print("🚀 Starting Slack Decision Agent...")
    print("📊 Features enabled:")
    print("   ✅ Decision proposals")
    print("   ✅ Anonymous voting (--anonymous, --anon, -a)")
    print("   ✅ Vote tracking")
    print("   ✅ Decision management")
    print("\n🌐 Server will start on http://0.0.0.0:8000")
    print("📡 Slack commands endpoint: http://0.0.0.0:8000/slack/commands")
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