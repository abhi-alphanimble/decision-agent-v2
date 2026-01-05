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
    ZOHO_DASHBOARD_HTML,
    ZOHO_CARD_CONNECTED,
    ZOHO_CARD_NOT_CONNECTED,
    SLACK_CARD_CONNECTED,
    SLACK_CARD_NOT_CONNECTED,
    SLACK_CARD_LOCKED,
    ALERT_SETUP_HTML,
    COMMANDS_SECTION_HTML
)
from ..templates import PRIVACY_POLICY_HTML, SUPPORT_PAGE_HTML, TERMS_OF_SERVICE_HTML
from ..templates_docs import ADMIN_GUIDE_HTML, USER_GUIDE_HTML, HELP_DOCUMENT_HTML, CASE_STUDIES_HTML

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
    """
    # Support both orgId (Zoho Web Tab) and org_id (OAuth flow)
    # orgId takes precedence if both are provided
    effective_org_id = orgId or org_id
    
    try:
        # Initialize variables
        zoho_card_html = ZOHO_CARD_NOT_CONNECTED
        slack_card_html = SLACK_CARD_LOCKED
        header_title = "Integration Setup"
        header_subtitle = "Connect your data sources to get started"
        alert_html = ALERT_SETUP_HTML
        commands_html = ""
        
        zoho_install = None
        
        # =====================================================================
        # ZOHO CRM SECTION
        # =====================================================================
        
        if effective_org_id:
            zoho_install = db.query(ZohoInstallation).filter(
                ZohoInstallation.zoho_org_id == effective_org_id
            ).first()
            
            if zoho_install:
                # Zoho IS connected
                zoho_card_html = ZOHO_CARD_CONNECTED.format(
                    org_id=effective_org_id,
                    data_center=zoho_install.zoho_domain.split('.')[-1].upper() if zoho_install.zoho_domain else "US",
                    connected_date=zoho_install.installed_at.strftime('%b %d, %Y')
                )
                
                # Check for Slack connection if Zoho is connected
                slack_install = db.query(SlackInstallation).filter(
                    SlackInstallation.zoho_org_id == effective_org_id
                ).first()
                
                if slack_install:
                    # Slack IS connected
                    slack_card_html = SLACK_CARD_CONNECTED.format(
                        workspace_name=slack_install.team_name or slack_install.team_id,
                        team_id=slack_install.team_id,
                        connected_date=slack_install.installed_at.strftime('%b %d, %Y') if slack_install.installed_at else "Recently",
                        org_id=effective_org_id
                    )
                    
                    # Update header and other sections for "After Connect" state
                    header_title = "Integrations"
                    header_subtitle = "Your systems are connected and synchronizing."
                    alert_html = "" # No alert setup needed
                    commands_html = COMMANDS_SECTION_HTML
                    
                else:
                    # Slack is NOT connected, but Zoho is
                    slack_card_html = SLACK_CARD_NOT_CONNECTED.format(org_id=effective_org_id)
                    # Alert is removed once Zoho is connected, even if Slack isn't
                    alert_html = "" 
        
        # =====================================================================
        # RENDER DASHBOARD
        # =====================================================================
        
        html_content = ZOHO_DASHBOARD_HTML.format(
            team_id=effective_org_id or "N/A",
            header_title=header_title,
            header_subtitle=header_subtitle,
            alert_html=alert_html,
            zoho_card_html=zoho_card_html,
            slack_card_html=slack_card_html,
            commands_html=commands_html
        )
        
        # Return response with headers allowing Zoho iframe embedding
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

@dashboard_router.get("/privacy", response_class=HTMLResponse)
async def privacy_policy(
    orgId: Optional[str] = Query(None, description="Zoho organization ID for back navigation"),
    org_id: Optional[str] = Query(None, description="Zoho organization ID (snake_case)")
):
    """Privacy Policy page - required for Slack App Directory."""
    from starlette.responses import Response
    
    # Support both orgId (Zoho Web Tab) and org_id (OAuth flow)
    effective_org_id = orgId or org_id or ""
    
    # Inject the org_id into the HTML template
    html_content = PRIVACY_POLICY_HTML.replace("{org_id}", effective_org_id)
    
    return Response(
        content=html_content,
        media_type="text/html",
        headers={
            "Content-Security-Policy": f"frame-ancestors 'self' {ZOHO_FRAME_ANCESTORS}"
        }
    )

@dashboard_router.get("/support", response_class=HTMLResponse)
async def support_page(
    orgId: Optional[str] = Query(None, description="Zoho organization ID for back navigation"),
    org_id: Optional[str] = Query(None, description="Zoho organization ID (snake_case)")
):
    """Support page - required for Slack App Directory."""
    from starlette.responses import Response
    
    # Support both orgId (Zoho Web Tab) and org_id (OAuth flow)
    effective_org_id = orgId or org_id or ""
    
    # Inject the org_id into the HTML template
    html_content = SUPPORT_PAGE_HTML.replace("{org_id}", effective_org_id)
    
    return Response(
        content=html_content,
        media_type="text/html",
        headers={
            "Content-Security-Policy": f"frame-ancestors 'self' {ZOHO_FRAME_ANCESTORS}"
        }
    )


@dashboard_router.get("/terms", response_class=HTMLResponse)
async def terms_of_service(
    orgId: Optional[str] = Query(None, description="Zoho organization ID for back navigation"),
    org_id: Optional[str] = Query(None, description="Zoho organization ID (snake_case)")
):
    """Terms of Service page - required for Zoho Marketplace submission."""
    from starlette.responses import Response
    
    # Support both orgId (Zoho Web Tab) and org_id (OAuth flow)
    effective_org_id = orgId or org_id or ""
    
    # Inject the org_id into the HTML template
    html_content = TERMS_OF_SERVICE_HTML.replace("{org_id}", effective_org_id)
    
    return Response(
        content=html_content,
        media_type="text/html",
        headers={
            "Content-Security-Policy": f"frame-ancestors 'self' {ZOHO_FRAME_ANCESTORS}"
        }
    )


@dashboard_router.get("/admin-guide", response_class=HTMLResponse)
async def admin_guide():
    """Admin Guide page - required for Zoho Marketplace submission."""
    return Response(
        content=ADMIN_GUIDE_HTML,
        media_type="text/html",
        headers={
            "Content-Security-Policy": f"frame-ancestors 'self' {ZOHO_FRAME_ANCESTORS}"
        }
    )


@dashboard_router.get("/user-guide", response_class=HTMLResponse)
async def user_guide():
    """User Guide page - required for Zoho Marketplace submission."""
    return Response(
        content=USER_GUIDE_HTML,
        media_type="text/html",
        headers={
            "Content-Security-Policy": f"frame-ancestors 'self' {ZOHO_FRAME_ANCESTORS}"
        }
    )


@dashboard_router.get("/help", response_class=HTMLResponse)
async def help_document():
    """Help Document page - required for Zoho Marketplace submission."""
    return Response(
        content=HELP_DOCUMENT_HTML,
        media_type="text/html",
        headers={
            "Content-Security-Policy": f"frame-ancestors 'self' {ZOHO_FRAME_ANCESTORS}"
        }
    )


@dashboard_router.get("/case-studies", response_class=HTMLResponse)
async def case_studies():
    """Case Studies page - required for Zoho Marketplace submission."""
    return Response(
        content=CASE_STUDIES_HTML,
        media_type="text/html",
        headers={
            "Content-Security-Policy": f"frame-ancestors 'self' {ZOHO_FRAME_ANCESTORS}"
        }
    )
