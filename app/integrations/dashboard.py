"""
Integration Dashboard Routes

Provides a web-based interface for managing Zoho CRM and Slack connections.
Flow: Connect Zoho CRM FIRST, then Slack.
Uses org_id (zoho_org_id) as the primary identifier.

Supports embedding in Zoho CRM Web Tab:
- URL: /dashboard?orgId=${zoho.org.organization_id}
- Allows iframe embedding from Zoho domains
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import HTMLResponse
from starlette.responses import Response
from sqlalchemy.orm import Session

from ..dependencies import get_db
from ..models import SlackInstallation, ZohoInstallation
from ..config.config import config
from ..templates_zoho import (
    ZOHO_ERROR_PAGE_HTML,
    ZOHO_DASHBOARD_HTML
)

logger = logging.getLogger(__name__)

# Create router
dashboard_router = APIRouter(prefix="", tags=["dashboard"])

# Zoho domains that can embed this dashboard in an iframe
ZOHO_FRAME_ANCESTORS = (
    "https://*.zoho.com https://*.zoho.in https://*.zoho.eu "
    "https://*.zoho.com.au https://*.zoho.jp https://*.zoho.com.cn "
    "https://*.zohocrm.com https://*.zohocrm.in https://*.zohocrm.eu "
    "https://*.zohocrm.com.au https://*.zohocrm.jp https://*.zohocrm.com.cn "
    "https://*.zohosandbox.com https://*.zohoplatform.com"
)


def build_slack_oauth_url(org_id: str) -> str:
    """
    Build the Slack OAuth URL for connecting Slack.
    Includes org_id in state for linking to Zoho organization.
    """
    # The actual OAuth URL is built in the slack_install endpoint
    # This just returns the install endpoint URL with org_id
    return f"/slack/install?org_id={org_id}"


def build_slack_success_html(team_name: str) -> str:
    """
    Build the Slack success message HTML shown when Slack is connected.
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


def build_zoho_success_html(org_id: str) -> str:
    """
    Build the Zoho CRM success message HTML shown when Zoho is connected.
    """
    return f"""
        <div class="success-card success-card-zoho">
            <div class="success-header">
                <span class="success-icon">✓</span>
                <span class="success-title">Zoho CRM Connected</span>
            </div>
            <div class="success-subtitle">Organization ID: <strong>{org_id}</strong></div>
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
                    <span>Organization-wide integration</span>
                </div>
            </div>
        </div>
    """


@dashboard_router.get("/dashboard", response_class=HTMLResponse)
async def show_dashboard(
    orgId: Optional[str] = Query(None, description="Zoho organization ID (camelCase for Zoho Web Tab)"),
    org_id: Optional[str] = Query(None, description="Zoho organization ID (snake_case for OAuth flow)"),
    db: Session = Depends(get_db)
):
    """
    Show integrations dashboard.
    
    Supports two URL formats:
    - /dashboard?orgId=xxx (Zoho CRM Web Tab format)
    - /dashboard?org_id=xxx (OAuth redirect format)
    
    Flow:
    1. Without org_id: Shows "Connect to Zoho CRM" button, Slack disabled
    2. With org_id: Shows Zoho as connected, Slack connection available
    
    Displays (in order):
    - Zoho CRM connection status (connect FIRST)
    - Slack connection status (connect SECOND, after Zoho)
    - Success messages below each card when connected
    """
    # Support both orgId (Zoho Web Tab) and org_id (OAuth flow)
    # orgId takes precedence if both are provided
    effective_org_id = orgId or org_id
    
    try:
        # Initialize variables
        slack_success_html = ""
        zoho_success_html = ""
        org_name = "Not Connected"
        
        # =====================================================================
        # ZOHO CRM SECTION - FIRST (Primary connection)
        # =====================================================================
        
        if effective_org_id:
            # org_id provided - check if Zoho is actually connected
            zoho_install = db.query(ZohoInstallation).filter(
                ZohoInstallation.zoho_org_id == effective_org_id
            ).first()
            
            if zoho_install:
                # Zoho IS connected
                org_name = f"Org: {effective_org_id}"
                zoho_status_class = "status-connected"
                zoho_status_text = "Connected"
                zoho_description = "Your Zoho CRM is connected. Decisions will sync automatically."
                
                zoho_info_html = f"""
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="info-label">Status</span>
                            <span class="info-value">✅ Active</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Organization ID</span>
                            <span class="info-value">{effective_org_id}</span>
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
                
                # Disconnect button - opens in new tab to avoid iframe issues
                zoho_action_button = f"""
                    <form action="/zoho/disconnect" method="post" target="_blank" target="_blank" onsubmit="return confirm('Are you sure you want to disconnect Zoho CRM? This will also disconnect Slack and delete all data.');">
                        <input type="hidden" name="org_id" value="{effective_org_id}">
                        <button type="submit" class="btn btn-danger">Disconnect Zoho CRM</button>
                    </form>
                """
                
                zoho_success_html = build_zoho_success_html(effective_org_id)
            else:
                # org_id provided but not found - treat as not connected
                zoho_status_class = "status-disconnected"
                zoho_status_text = "Not Connected"
                zoho_description = "Connect your Zoho CRM to get started with Decision Agent."
                
                zoho_info_html = """
                    <div class="alert alert-info">
                        <span class="alert-icon">💡</span>
                        <div>
                            <strong>Why connect Zoho CRM?</strong><br>
                            Decision Agent syncs all team decisions to your Zoho CRM. 
                            Track decision-making progress alongside your business data.
                        </div>
                    </div>
                """
                
                zoho_action_button = '<button onclick="startZohoOAuth()" class="btn btn-primary">Connect Zoho CRM</button>'
                zoho_success_html = ""
        else:
            # No org_id - Zoho not connected yet
            zoho_status_class = "status-disconnected"
            zoho_status_text = "Not Connected"
            zoho_description = "Connect your Zoho CRM to get started with Decision Agent."
            
            zoho_info_html = """
                <div class="alert alert-info">
                    <span class="alert-icon">💡</span>
                    <div>
                        <strong>Why connect Zoho CRM?</strong><br>
                        Decision Agent syncs all team decisions to your Zoho CRM. 
                        Track decision-making progress alongside your business data.
                    </div>
                </div>
            """
            
            zoho_action_button = '<button onclick="startZohoOAuth()" class="btn btn-primary">Connect Zoho CRM</button>'
            zoho_success_html = ""
        
        # =====================================================================
        # SLACK SECTION - SECOND (Requires Zoho to be connected first)
        # =====================================================================
        
        zoho_is_connected = effective_org_id and db.query(ZohoInstallation).filter(
            ZohoInstallation.zoho_org_id == effective_org_id
        ).first() is not None
        
        if zoho_is_connected:
            # Check Slack installation linked to this Zoho org
            slack_install = db.query(SlackInstallation).filter(
                SlackInstallation.zoho_org_id == effective_org_id
            ).first()
            
            if slack_install:
                # Slack IS connected
                team_name = slack_install.team_name or slack_install.team_id
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
                            <span class="info-label">Workspace</span>
                            <span class="info-value">{team_name}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Team ID</span>
                            <span class="info-value">{slack_install.team_id}</span>
                        </div>
                    </div>
                """
                
                slack_action_button = ""  # No disconnect for Slack (disconnecting Zoho removes everything)
                slack_success_html = build_slack_success_html(team_name)
                
                alert_html = ""  # All connected, no alerts
                
            else:
                # Slack is NOT connected, but Zoho is
                slack_status_class = "status-disconnected"
                slack_status_text = "Not Connected"
                slack_description = "Connect your Slack workspace to start using Decision Agent."
                
                slack_info_html = """
                    <div class="alert alert-info">
                        <span class="alert-icon">💡</span>
                        <div>
                            <strong>Why connect Slack?</strong><br>
                            Decision Agent helps your team make decisions collaboratively in Slack. 
                            Connect your workspace to start using slash commands.
                        </div>
                    </div>
                """
                
                slack_oauth_url = build_slack_oauth_url(effective_org_id)
                slack_action_button = f'<a href="{slack_oauth_url}" class="btn btn-primary" target="_blank">Connect to Slack</a>'
                slack_success_html = ""
                
                # Show alert to connect Slack
                alert_html = """
                    <div class="alert alert-warning">
                        <span class="alert-icon">⚠️</span>
                        <div>
                            <strong>Slack not connected</strong><br>
                            Connect your Slack workspace below to start using Decision Agent.
                        </div>
                    </div>
                """
        else:
            # Zoho is NOT connected - disable Slack section
            slack_status_class = "status-disconnected"
            slack_status_text = "Not Available"
            slack_description = "Connect Zoho CRM first to enable Slack integration."
            
            slack_info_html = """
                <div class="alert alert-info">
                    <span class="alert-icon">🔒</span>
                    <div>
                        <strong>Zoho CRM connection required</strong><br>
                        You need to connect your Zoho CRM first before connecting Slack.
                    </div>
                </div>
            """
            
            slack_action_button = '<button class="btn btn-disabled" disabled>Connect to Slack</button>'
            slack_success_html = ""
            
            # Show welcome alert
            alert_html = """
                <div class="alert alert-warning">
                    <span class="alert-icon">👋</span>
                    <div>
                        <strong>Welcome to Decision Agent!</strong><br>
                        Please connect your Zoho CRM first to get started.
                    </div>
                </div>
            """
        
        # =====================================================================
        # RENDER DASHBOARD
        # =====================================================================
        
        html_content = ZOHO_DASHBOARD_HTML.format(
            team_name=org_name,
            team_id=effective_org_id or "N/A",
            # Zoho placeholders (shown FIRST)
            zoho_status_class=zoho_status_class,
            zoho_status_text=zoho_status_text,
            zoho_description=zoho_description,
            zoho_info_html=zoho_info_html,
            zoho_action_button=zoho_action_button,
            zoho_success_html=zoho_success_html,
            # Slack placeholders (shown SECOND)
            slack_status_class=slack_status_class,
            slack_status_text=slack_status_text,
            slack_description=slack_description,
            slack_info_html=slack_info_html,
            slack_action_button=slack_action_button,
            slack_success_html=slack_success_html,
            alert_html=alert_html
        )
        
        # Return response with headers allowing Zoho iframe embedding
        # Note: X-Frame-Options is omitted - using CSP frame-ancestors instead (modern approach)
        return Response(
            content=html_content,
            media_type="text/html",
            headers={
                "Content-Security-Policy": f"frame-ancestors 'self' {ZOHO_FRAME_ANCESTORS}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error showing dashboard for org {effective_org_id}: {e}", exc_info=True)
        return Response(
            content=ZOHO_ERROR_PAGE_HTML.format(
                error_message=f"An error occurred: {str(e)}",
                retry_url=f"/dashboard?org_id={effective_org_id}" if effective_org_id else "/dashboard"
            ),
            media_type="text/html",
            status_code=500,
            headers={
                "Content-Security-Policy": f"frame-ancestors 'self' {ZOHO_FRAME_ANCESTORS}"
            }
        )
