"""
Slack OAuth endpoints for app installation.

Slack is connected SECOND, after Zoho CRM.
The org_id (zoho_org_id) must be provided to link Slack to the Zoho organization.
"""
from typing import Optional
import secrets
import base64
from datetime import datetime, timedelta, UTC
from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
import logging

from fastapi import APIRouter

from ..config import config
from ..dependencies import get_db
from ..models import SlackInstallation, ZohoInstallation
from ..utils import get_utc_now
from ..templates_zoho import ZOHO_OAUTH_SUCCESS_HTML
from slack_sdk.web import WebClient

logger = logging.getLogger(__name__)

# Create router for Slack OAuth endpoints
router = APIRouter()


# ============================================================================
# STATE CACHE FOR CSRF PROTECTION
# ============================================================================

# In-memory cache for OAuth state nonces
# Format: {nonce: {"org_id": str, "created_at": datetime, "expires_at": datetime}}
_slack_state_cache: dict[str, dict] = {}

# State expiration time (15 minutes)
STATE_EXPIRATION_MINUTES = 15


def _cleanup_expired_states() -> None:
    """Remove expired state entries from cache."""
    now = datetime.now(UTC)
    expired_nonces = [
        nonce for nonce, data in _slack_state_cache.items()
        if data["expires_at"] <= now
    ]
    
    for nonce in expired_nonces:
        del _slack_state_cache[nonce]
    
    if expired_nonces:
        logger.debug(f"Cleaned up {len(expired_nonces)} expired Slack state nonce(s)")


def generate_slack_state(org_id: str) -> str:
    """
    Generate a secure state parameter for Slack OAuth flow.
    
    Args:
        org_id: Zoho organization ID to link Slack workspace to
        
    Returns:
        Base64-encoded state string
    """
    _cleanup_expired_states()
    
    nonce = secrets.token_urlsafe(16)
    state_data = f"{org_id}:{nonce}"
    state = base64.urlsafe_b64encode(state_data.encode()).decode()
    
    now = datetime.now(UTC)
    _slack_state_cache[nonce] = {
        "org_id": org_id,
        "created_at": now,
        "expires_at": now + timedelta(minutes=STATE_EXPIRATION_MINUTES)
    }
    
    logger.debug(f"Generated Slack state for org {org_id}, nonce: {nonce[:8]}...")
    return state


def verify_and_consume_slack_state(state: str) -> Optional[str]:
    """
    Verify Slack state parameter and consume the nonce.
    
    Returns:
        org_id if state is valid, None otherwise
    """
    try:
        state_data = base64.urlsafe_b64decode(state.encode()).decode()
        org_id, nonce = state_data.split(":", 1)
        
        if nonce not in _slack_state_cache:
            logger.warning(f"Invalid or reused Slack nonce: {nonce[:8]}...")
            return None
        
        cache_entry = _slack_state_cache[nonce]
        
        now = datetime.now(UTC)
        if now > cache_entry["expires_at"]:
            logger.warning(f"Expired Slack nonce: {nonce[:8]}...")
            del _slack_state_cache[nonce]
            return None
        
        if cache_entry["org_id"] != org_id:
            logger.error(f"Org ID mismatch in Slack state!")
            return None
        
        del _slack_state_cache[nonce]
        logger.info(f"✅ Slack state verified for org {org_id}")
        return org_id
        
    except Exception as e:
        logger.error(f"Failed to verify Slack state: {e}")
        return None


@router.get("/slack/install")
async def slack_install(request: Request, org_id: str):
    """
    Initiates the Slack OAuth 2.0 installation flow.
    Requires org_id (Zoho organization ID) to link the Slack workspace.
    
    Query parameters:
        org_id: Zoho organization ID (required)
    """
    if not org_id:
        raise HTTPException(
            status_code=400,
            detail="org_id parameter is required. Connect Zoho CRM first."
        )
    
    # Scopes required for the bot
    scopes = [
        "chat:write",
        "commands",
        "app_mentions:read",
        "channels:history",
        "groups:history",
        "im:history",
        "mpim:history",
        "chat:write.public",
        "users:read",
        "channels:read",
        "groups:read",
        "team:read",
        "channels:join",
        "mpim:read"
    ]
    
    # Generate state with org_id for CSRF protection
    state = generate_slack_state(org_id)
    
    # Build redirect URI
    redirect_uri = f"{config.APP_BASE_URL}/slack/install/callback"
    
    # Build the OAuth URL
    oauth_url = (
        f"https://slack.com/oauth/v2/authorize"
        f"?client_id={config.SLACK_CLIENT_ID}"
        f"&scope={','.join(scopes)}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
        f"&user_scope="
    )
    
    logger.info(f"Initiating Slack OAuth for org {org_id}")
    return RedirectResponse(url=oauth_url)


@router.get("/slack/install/callback")
async def slack_callback(
    request: Request, 
    code: Optional[str] = None, 
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Handles the Slack OAuth 2.0 redirect after a user approves the app installation.
    Links the Slack workspace to the Zoho organization via org_id in state.
    """
    if error:
        logger.error(f"❌ Slack OAuth error: {error}")
        return HTMLResponse(
            content=f"""
            <html>
            <head><title>Installation Failed</title></head>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>❌ Slack Installation Failed</h1>
                <p>Error: {error}</p>
                <a href="/dashboard">Return to Dashboard</a>
            </body>
            </html>
            """,
            status_code=400
        )
    
    if not code:
        logger.error("❌ No code received from Slack")
        return HTMLResponse(
            content="""
            <html>
            <head><title>Installation Failed</title></head>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>❌ Slack Installation Failed</h1>
                <p>No authorization code received.</p>
                <a href="/dashboard">Return to Dashboard</a>
            </body>
            </html>
            """,
            status_code=400
        )
    
    if not state:
        logger.error("❌ No state parameter received from Slack")
        return HTMLResponse(
            content="""
            <html>
            <head><title>Installation Failed</title></head>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>❌ Slack Installation Failed</h1>
                <p>Missing state parameter (CSRF protection).</p>
                <a href="/dashboard">Return to Dashboard</a>
            </body>
            </html>
            """,
            status_code=400
        )
    
    # Verify state and get org_id
    org_id = verify_and_consume_slack_state(state)
    if not org_id:
        logger.error("❌ State verification failed")
        return HTMLResponse(
            content="""
            <html>
            <head><title>Installation Failed</title></head>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>❌ Slack Installation Failed</h1>
                <p>State verification failed. The OAuth flow may have expired. Please try again.</p>
                <a href="/dashboard">Return to Dashboard</a>
            </body>
            </html>
            """,
            status_code=400
        )
    
    # Verify Zoho organization exists
    zoho_install = db.query(ZohoInstallation).filter(
        ZohoInstallation.zoho_org_id == org_id
    ).first()
    
    if not zoho_install:
        logger.error(f"❌ Zoho org {org_id} not found")
        return HTMLResponse(
            content=f"""
            <html>
            <head><title>Installation Failed</title></head>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>❌ Slack Installation Failed</h1>
                <p>Zoho organization not found. Please connect Zoho CRM first.</p>
                <a href="/dashboard">Return to Dashboard</a>
            </body>
            </html>
            """,
            status_code=400
        )

    try:
        # 1. Exchange the temporary code for permanent tokens
        # NOTE: redirect_uri must match exactly what was used in the authorization request
        redirect_uri = f"{config.APP_BASE_URL}/slack/install/callback"
        client = WebClient()
        oauth_response = client.oauth_v2_access(
            client_id=config.SLACK_CLIENT_ID,
            client_secret=config.SLACK_CLIENT_SECRET,
            code=code,
            redirect_uri=redirect_uri,
        )
        
        # 2. Extract the necessary tokens/IDs
        team_id = oauth_response["team"]["id"]
        team_name = oauth_response["team"]["name"]
        bot_token = oauth_response["access_token"]
        bot_user_id = oauth_response["bot_user_id"]
        
        logger.info(f"🔑 Successfully installed in Team ID: {team_id} ({team_name})")
        logger.info(f"💾 Linking Slack workspace {team_id} to Zoho org {org_id}")
        
        # Check if installation already exists
        installation = db.query(SlackInstallation).filter(
            SlackInstallation.team_id == team_id
        ).first()
        
        if installation:
            # Update existing installation
            installation.access_token = bot_token
            installation.bot_user_id = bot_user_id
            installation.team_name = team_name
            installation.zoho_org_id = org_id
            installation.installed_at = get_utc_now()
            logger.info(f"🔄 Updated existing installation for {team_name}")
        else:
            # Create new installation linked to Zoho org
            installation = SlackInstallation(
                team_id=team_id,
                team_name=team_name,
                access_token=bot_token,
                bot_user_id=bot_user_id,
                zoho_org_id=org_id
            )
            db.add(installation)
            logger.info(f"✨ Created new installation for {team_name} linked to org {org_id}")
            
        db.commit()
        
        # Return success page that closes popup and signals parent to refresh
        logger.info(f"🔄 Showing success page for Slack {team_name}, org {org_id}")
        return HTMLResponse(
            content=ZOHO_OAUTH_SUCCESS_HTML.format(
                service_name=f"Slack ({team_name})",
                service_type="slack",
                org_id=org_id
            ),
            status_code=200
        )

    except Exception as e:
        logger.error(f"❌ OAuth Access Error: {e}", exc_info=True)
        db.rollback()
        return HTMLResponse(
            content=f"""
            <html>
            <head><title>Installation Failed</title></head>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>❌ Slack Installation Failed</h1>
                <p>Error: {str(e)}</p>
                <a href="/dashboard?org_id={org_id}">Return to Dashboard</a>
            </body>
            </html>
            """,
            status_code=500
        )
