"""
Zoho Integration Dashboard Routes

Provides a web-based interface for managing Slack and Zoho CRM connections.
Supports both connected and not-connected states for Slack.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..models import SlackInstallation, ZohoInstallation
from ..config.config import config
from ..templates_zoho import (
    ZOHO_SUCCESS_PAGE_HTML,
    ZOHO_ERROR_PAGE_HTML,
    ZOHO_DASHBOARD_HTML
)

logger = logging.getLogger(__name__)

# Create router
dashboard_router = APIRouter(prefix="", tags=["dashboard"])


def build_slack_oauth_url() -> str:
    """
    Build the Slack OAuth URL for connecting Slack.
    Uses the shareable URL format with all required scopes.
    """
    scopes = [
        "app_mentions:read",
        "channels:history", 
        "chat:write",
        "commands",
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
    
    # Build redirect URI - after OAuth, redirect back to dashboard
    redirect_uri = f"{config.APP_BASE_URL}/slack/install/callback"
    
    oauth_url = (
        f"https://slack.com/oauth/v2/authorize"
        f"?client_id={config.SLACK_CLIENT_ID}"
        f"&scope={','.join(scopes)}"
        f"&redirect_uri={redirect_uri}"
        f"&user_scope="
    )
    
    return oauth_url


def build_slack_success_html(team_name: str) -> str:
    """
    Build the Slack success message HTML shown when Slack is connected.
    Minimal style with light colors.
    """
    return f"""
        <div class="success-card success-card-slack">
            <div class="success-header">
                <span class="success-icon">✓</span>
                <span class="success-title">Slack Connected</span>
            </div>
            <div class="success-subtitle">Decision Agent is installed to <strong>{team_name}</strong></div>
            <div class="success-commands">
                <div class="success-commands-title">Quick Start Commands:</div>
                <div class="command-item">/decision help</div>
                <div class="command-item">/decision propose "Your proposal"</div>
                <div class="command-item">/decision list</div>
            </div>
        </div>
    """


def build_zoho_success_html(team_name: str) -> str:
    """
    Build the Zoho CRM success message HTML shown when Zoho is connected.
    Minimal style with light colors.
    """
    return f"""
        <div class="success-card success-card-zoho">
            <div class="success-header">
                <span class="success-icon">✓</span>
                <span class="success-title">Zoho CRM Connected</span>
            </div>
            <div class="success-subtitle">Connected to team: <strong>{team_name}</strong></div>
            <div class="success-features">
                <div class="success-feature">
                    <span class="success-feature-icon">🔄</span>
                    <span>Automatic sync enabled</span>
                </div>
                <div class="success-feature">
                    <span class="success-feature-icon">🔐</span>
                    <span>Credentials encrypted</span>
                </div>
                <div class="success-feature">
                    <span class="success-feature-icon">👥</span>
                    <span>Team-wide integration</span>
                </div>
            </div>
        </div>
    """


@dashboard_router.get("/dashboard", response_class=HTMLResponse)
async def show_dashboard(
    team_id: Optional[str] = Query(None, description="Slack team ID (optional - if not provided, shows Slack connection button)"),
    db: Session = Depends(get_db)
):
    """
    Show integrations dashboard for a team.
    
    Two modes:
    1. Without team_id: Shows "Connect to Slack" button, Zoho CRM disabled
    2. With team_id: Shows Slack as connected, Zoho CRM connection available
    
    Displays:
    - Slack connection status (connected or not)
    - Zoho CRM connection status
    - Success messages below each card when connected
    - Buttons to connect/disconnect integrations
    """
    try:
        # Initialize success HTML variables
        slack_success_html = ""
        zoho_success_html = ""
        
        # =====================================================================
        # SLACK SECTION - Dynamic based on team_id presence
        # =====================================================================
        
        if team_id:
            # team_id provided - check if Slack is actually installed
            slack_install = db.query(SlackInstallation).filter(
                SlackInstallation.team_id == team_id
            ).first()
            
            if slack_install:
                # Slack IS connected
                team_name = slack_install.team_name or team_id
                slack_status_class = "status-connected"
                slack_status_text = "Connected"
                slack_description = "Your Slack workspace is connected to Decision Agent."
                
                slack_info_html = f"""
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">Status</span>
                            <span class="info-value">✅ Active</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Team ID</span>
                            <span class="info-value">{team_id}</span>
                        </div>
                    </div>
                """
                
                # No action button when connected (or could add disconnect option later)
                slack_action_button = ""
                
                # Build Slack success message HTML
                slack_success_html = build_slack_success_html(team_name)
                
            else:
                # team_id provided but Slack not found - treat as not connected
                team_name = "Not Connected"
                slack_status_class = "status-disconnected"
                slack_status_text = "Not Connected"
                slack_description = "Connect your Slack workspace to get started with Decision Agent."
                
                slack_info_html = """
                    <div class="alert alert-info">
                        <span class="alert-icon">💡</span>
                        <div>
                            <strong>Why connect Slack?</strong><br>
                            Decision Agent helps your team make decisions collaboratively in Slack. 
                            Connect your workspace to start using slash commands for proposing and voting on decisions.
                        </div>
                    </div>
                """
                
                slack_oauth_url = build_slack_oauth_url()
                slack_action_button = f'<a href="{slack_oauth_url}" class="btn btn-primary">Connect to Slack</a>'
                
                # No success message when not connected
                slack_success_html = ""
        else:
            # No team_id - Slack not connected yet
            team_name = "Not Connected"
            slack_status_class = "status-disconnected"
            slack_status_text = "Not Connected"
            slack_description = "Connect your Slack workspace to get started with Decision Agent."
            
            slack_info_html = """
                <div class="alert alert-info">
                    <span class="alert-icon">💡</span>
                    <div>
                        <strong>Why connect Slack?</strong><br>
                        Decision Agent helps your team make decisions collaboratively in Slack. 
                        Connect your workspace to start using slash commands for proposing and voting on decisions.
                    </div>
                </div>
            """
            
            slack_oauth_url = build_slack_oauth_url()
            slack_action_button = f'<a href="{slack_oauth_url}" class="btn btn-primary">Connect to Slack</a>'
            
            # No success message when not connected
            slack_success_html = ""
        
        # =====================================================================
        # ZOHO CRM SECTION - Only enabled when Slack is connected
        # =====================================================================
        
        slack_is_connected = team_id and db.query(SlackInstallation).filter(
            SlackInstallation.team_id == team_id
        ).first() is not None
        
        if slack_is_connected:
            # Check Zoho installation
            zoho_install = db.query(ZohoInstallation).filter(
                ZohoInstallation.team_id == team_id
            ).first()
            
            if zoho_install:
                # Zoho is connected
                zoho_status_class = "status-connected"
                zoho_status_text = "Connected"
                zoho_description = "Your team's Zoho CRM is connected. All decisions will sync automatically."
                
                # Show Zoho info
                zoho_info_html = f"""
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">Status</span>
                            <span class="info-value">✅ Active</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Zoho Organization</span>
                            <span class="info-value">{zoho_install.zoho_org_id or 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Data Center</span>
                            <span class="info-value">{zoho_install.zoho_domain.upper()}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Connected Since</span>
                            <span class="info-value">{zoho_install.installed_at.strftime('%B %d, %Y')}</span>
                        </div>
                    </div>
                """
                
                # Disconnect button
                zoho_action_button = f"""
                    <form action="/zoho/disconnect" method="post" onsubmit="return confirm('Are you sure you want to disconnect Zoho CRM? Decisions will no longer sync.');">
                        <input type="hidden" name="team_id" value="{team_id}">
                        <button type="submit" class="btn btn-danger">Disconnect Zoho CRM</button>
                    </form>
                """
                
                alert_html = ""
                
                # Build Zoho success message HTML
                zoho_success_html = build_zoho_success_html(team_name)
                
            else:
                # Zoho is NOT connected, but Slack is
                zoho_status_class = "status-disconnected"
                zoho_status_text = "Not Connected"
                zoho_description = "Connect your Zoho CRM to automatically sync all team decisions."
                
                zoho_info_html = """
                    <div class="alert alert-info">
                        <span class="alert-icon">💡</span>
                        <div>
                            <strong>Why connect Zoho CRM?</strong><br>
                            Automatically sync all decisions and votes to your Zoho CRM account. 
                            Track decision-making progress alongside your business data.
                        </div>
                    </div>
                """
                
                # Connect button
                connect_url = f"/zoho/install?team_id={team_id}"
                zoho_action_button = f'<a href="{connect_url}" class="btn btn-primary">Connect Zoho CRM</a>'
                
                # Show alert on dashboard
                alert_html = """
                    <div class="alert alert-warning">
                        <span class="alert-icon">⚠️</span>
                        <div>
                            <strong>Zoho CRM not connected</strong><br>
                            Connect your Zoho CRM below to start syncing decisions automatically.
                        </div>
                    </div>
                """
                
                # No Zoho success message when not connected
                zoho_success_html = ""
        else:
            # Slack is NOT connected - disable Zoho CRM section
            zoho_status_class = "status-disconnected"
            zoho_status_text = "Not Available"
            zoho_description = "Connect Slack first to enable Zoho CRM integration."
            
            zoho_info_html = """
                <div class="alert alert-info">
                    <span class="alert-icon">🔒</span>
                    <div>
                        <strong>Slack connection required</strong><br>
                        You need to connect your Slack workspace first before connecting Zoho CRM.
                    </div>
                </div>
            """
            
            # Disabled button
            zoho_action_button = '<button class="btn btn-disabled" disabled>Connect Zoho CRM</button>'
            
            # Show alert to connect Slack first
            alert_html = """
                <div class="alert alert-warning">
                    <span class="alert-icon">👋</span>
                    <div>
                        <strong>Welcome to Decision Agent!</strong><br>
                        Please connect your Slack workspace first to get started.
                    </div>
                </div>
            """
            
            # No Zoho success message when Slack not connected
            zoho_success_html = ""
        
        # =====================================================================
        # RENDER DASHBOARD
        # =====================================================================
        
        html_content = ZOHO_DASHBOARD_HTML.format(
            team_name=team_name,
            team_id=team_id or "N/A",
            # Slack placeholders
            slack_status_class=slack_status_class,
            slack_status_text=slack_status_text,
            slack_description=slack_description,
            slack_info_html=slack_info_html,
            slack_action_button=slack_action_button,
            slack_success_html=slack_success_html,
            # Zoho placeholders
            zoho_status_class=zoho_status_class,
            zoho_status_text=zoho_status_text,
            zoho_description=zoho_description,
            zoho_info_html=zoho_info_html,
            zoho_action_button=zoho_action_button,
            zoho_success_html=zoho_success_html,
            alert_html=alert_html
        )
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Error showing dashboard for team {team_id}: {e}", exc_info=True)
        return HTMLResponse(
            content=ZOHO_ERROR_PAGE_HTML.format(
                error_message=f"An error occurred: {str(e)}",
                retry_url=f"/dashboard?team_id={team_id}" if team_id else "/dashboard"
            ),
            status_code=500
        )
