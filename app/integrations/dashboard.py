"""
Zoho Integration Dashboard Routes

Provides a web-based interface for managing Zoho CRM connections.
"""
import logging
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


@dashboard_router.get("/dashboard", response_class=HTMLResponse)
async def show_dashboard(
    team_id: str = Query(..., description="Slack team ID"),
    db: Session = Depends(get_db)
):
    """
    Show integrations dashboard for a team.
    
    Displays:
    - Slack connection status (always connected)
    - Zoho CRM connection status
    - Buttons to connect/disconnect integrations
    """
    try:
        # Get Slack installation
        slack_install = db.query(SlackInstallation).filter(
            SlackInstallation.team_id == team_id
        ).first()
        
        if not slack_install:
            return HTMLResponse(
                content=ZOHO_ERROR_PAGE_HTML.format(
                    error_message="Team not found. Please install the Slack app first.",
                    retry_url="/slack/install"
                ),
                status_code=404
            )
        
        team_name = slack_install.team_name or team_id
        
        # Check Zoho installation
        zoho_install = db.query(ZohoInstallation).filter(
            ZohoInstallation.team_id == team_id
        ).first()
        
        # Build Zoho-specific HTML
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
            
        else:
            # Zoho is NOT connected
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
        
        # Render dashboard
        html_content = ZOHO_DASHBOARD_HTML.format(
            team_name=team_name,
            team_id=team_id,
            zoho_status_class=zoho_status_class,
            zoho_status_text=zoho_status_text,
            zoho_description=zoho_description,
            zoho_info_html=zoho_info_html,
            zoho_action_button=zoho_action_button,
            alert_html=alert_html
        )
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Error showing dashboard for team {team_id}: {e}", exc_info=True)
        return HTMLResponse(
            content=ZOHO_ERROR_PAGE_HTML.format(
                error_message=f"An error occurred:  {str(e)}",
                retry_url=f"/dashboard?team_id={team_id}"
            ),
            status_code=500
        )
