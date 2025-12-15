"""
Zoho CRM API client for Decision Agent integration.
Handles OAuth token management and API requests with multi-tenant support.

Each Slack team has their own Zoho CRM connection stored in the database.
"""
import logging
import os
from datetime import datetime, timedelta, UTC
import requests
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models import ZohoInstallation
from ..utils.encryption import decrypt_token, encrypt_token

logger = logging.getLogger(__name__)


class ZohoCRMClient:
    """
    Multi-tenant Zoho CRM API client with OAuth 2.0 support.
    
    Each instance is tied to a specific Slack team and uses that team's
    Zoho credentials from the database.
    """

    def __init__(self, team_id: str, db: Session):
        """
        Initialize Zoho CRM client for a specific team.
        
        Args:
            team_id: Slack team ID
            db: Database session
            
        Raises:
            ValueError: If team has no Zoho installation
        """
        self.team_id = team_id
        self.db = db
        
        # Fetch Zoho installation from database
        self.installation = db.query(ZohoInstallation).filter(
            ZohoInstallation.team_id == team_id
        ).first()
        
        if not self.installation:
            raise ValueError(f"Team {team_id} has no Zoho CRM connection")
        
        # Get OAuth credentials from environment (app-level, same for all teams)
        self.client_id = os.getenv("ZOHO_CLIENT_ID", "")
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET", "")
        
        # Build API URLs based on team's data center
        domain = self.installation.zoho_domain or "com"
        self.api_domain = f"https://www.zohoapis.{domain}"
        self.accounts_url = f"https://accounts.zoho.{domain}"
        
        # Decrypt tokens from database
        self.access_token = decrypt_token(self.installation.access_token)
        self.refresh_token = decrypt_token(self.installation.refresh_token)
        self.token_expiry = self.installation.token_expires_at
        
        logger.debug(
            f"Initialized Zoho CRM client for team {team_id}, "
            f"org: {self.installation.zoho_org_id}, domain: {domain}"
        )
    
    def get_access_token(self) -> Optional[str]:
        """
        Get a valid access token, refreshing if necessary.
        Updates the database with new token on refresh.
        
        Returns:
            Access token string, or None if refresh fails
        """
        # Check if token is still valid (with 5-minute buffer)
        if self.access_token and self.token_expiry:
            now = datetime.now(UTC)
            if now < (self.token_expiry - timedelta(minutes=5)):
                logger.debug(f"Using cached access token for team {self.team_id}")
                return self.access_token
        
        # Refresh the token
        return self._refresh_access_token()
    
    def _refresh_access_token(self, max_retries: int = 3) -> Optional[str]:
        """
        Refresh the access token using the refresh token with retry logic.
        
        Handles different failure scenarios:
        - Network errors: Retry with exponential backoff
        - Revoked tokens: Log error, don't retry  
        - Zoho account issues: Log error, don't retry
        
        Updates the database with the new access token and expiry.
        
        Args:
            max_retries: Maximum number of retry attempts for transient errors
            
        Returns:
            New access token, or None if refresh fails
        """
        if not self.client_id or not self.client_secret:
            logger.error("ZOHO_CLIENT_ID or ZOHO_CLIENT_SECRET not configured")
            return None
        
        if not self.refresh_token:
            logger.error(f"No refresh token for team {self.team_id}")
            return None
        
        # Retry with exponential backoff for network errors
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** (attempt - 1)
                    logger.info(
                        f"Retrying token refresh for team {self.team_id} "
                        f"(attempt {attempt + 1}/{max_retries}) after {wait_time}s..."
                    )
                    import time
                    time.sleep(wait_time)
                
                logger.info(f"Refreshing Zoho access token for team {self.team_id}...")
                
                response = requests.post(
                    f"{self.accounts_url}/oauth/v2/token",
                    data={
                        "refresh_token": self.refresh_token,
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "grant_type": "refresh_token",
                    },
                    timeout=10
                )
                
                # Success case
                if response.status_code == 200:
                    data = response.json()
                    new_access_token = data.get("access_token")
                    expires_in = data.get("expires_in", 3600)  # Default 1 hour
                    
                    if not new_access_token:
                        logger.error("No access_token in refresh response")
                        return None
                    
                    # Update in-memory cache
                    self.access_token = new_access_token
                    self.token_expiry = datetime.now(UTC) + timedelta(seconds=expires_in)
                    
                    # Update database with encrypted token
                    self.installation.access_token = encrypt_token(new_access_token)
                    self.installation.token_expires_at = self.token_expiry
                    self.db.commit()
                    
                    logger.info(
                        f"✅ Zoho access token refreshed for team {self.team_id} "
                        f"(expires in {expires_in}s)"
                    )
                    return new_access_token
                
                # Permanent errors (don't retry)
                elif response.status_code in [400, 401]:
                    # 400 = Invalid grant (refresh token revoked/expired)
                    # 401 = Unauthorized (invalid client credentials)
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("error", response.text)
                    
                    logger.error(
                        f"❌ Permanent error refreshing token for team {self.team_id}: "
                        f"{response.status_code} - {error_msg}"
                    )
                    
                    # Check if it's a revoked/invalid refresh token
                    if "invalid" in error_msg.lower() or "revoked" in error_msg.lower():
                        logger.warning(
                            f"⚠️ Refresh token for team {self.team_id} is invalid/revoked. "
                            "Team needs to re-authorize via OAuth."
                        )
                        # Could mark installation as disconnected here if we add status field
                    
                    return None  # Don't retry permanent errors
                
                # Temporary errors (retry)
                elif response.status_code in [429, 500, 502, 503, 504]:
                    # 429 = Rate limit
                    # 5xx = Server errors
                    logger.warning(
                        f"⚠️ Temporary error refreshing token for team {self.team_id}: "
                        f"{response.status_code} - {response.text}"
                    )
                    
                    # Will retry (continue loop)
                    if attempt == max_retries - 1:
                        logger.error(
                            f"❌ Max retries reached for team {self.team_id}, giving up"
                        )
                        return None
                    continue
                
                # Other errors
                else:
                    logger.error(
                        f"❌ Unexpected error refreshing token for team {self.team_id}: "
                        f"{response.status_code} - {response.text}"
                    )
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(
                    f"⚠️ Timeout refreshing token for team {self.team_id} "
                    f"(attempt {attempt + 1}/{max_retries})"
                )
                if attempt == max_retries - 1:
                    logger.error(f"❌ Max retries reached (timeout), giving up")
                    return None
                continue
                
            except requests.exceptions.ConnectionError:
                logger.warning(
                    f"⚠️ Connection error refreshing token for team {self.team_id} "
                    f"(attempt {attempt + 1}/{max_retries})"
                )
                if attempt == max_retries - 1:
                    logger.error(f"❌ Max retries reached (connection error), giving up")
                    return None
                continue
                
            except Exception as e:
                logger.error(
                    f"❌ Unexpected exception refreshing token for team {self.team_id}: {e}",
                    exc_info=True
                )
                return None
        
        return None
    
    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Make an authenticated request to Zoho CRM API.
        
        Args:
            method: HTTP method (GET, POST, PUT)
            endpoint: API endpoint (e.g., "Decisions", "Decisions/123")
            data: Request payload for POST/PUT
            
        Returns:
            JSON response, or None if request fails
        """
        access_token = self.get_access_token()
        if not access_token:
            logger.error(f"Could not obtain access token for team {self.team_id}")
            return None
        
        url = f"{self.api_domain}/crm/v3/{endpoint}"
        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
            "Content-Type": "application/json",
        }
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=10)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None
            
            if response.status_code in [200, 201]:
                return response.json()
            else:
                logger.error(
                    f"API request failed for team {self.team_id}: "
                    f"{method} {endpoint} - {response.status_code}: {response.text}"
                )
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for team {self.team_id}: {e}", exc_info=True)
            return None
    
    def create_decision(self, decision_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new decision record in Zoho CRM.
        
        Args:
            decision_data: Decision data mapped to Zoho fields
            
        Returns:
            Zoho API response with created record details, or None if failed
        """
        # Wrap data in 'data' key as per Zoho API format
        payload = {"data": [decision_data]}
        result = self._make_request("POST", "Decisions", payload)
        
        if result and result.get("data"):
            record = result["data"][0]
            # Success if code is 0 or message is "record added"
            if record.get("code") == 0 or "added" in record.get("message", "").lower():
                logger.info(
                    f"✅ Created Zoho decision record for team {self.team_id}: "
                    f"{record.get('id')} | {record.get('message')}"
                )
                return record
            else:
                logger.error(
                    f"❌ Zoho API error for team {self.team_id}: "
                    f"{record.get('message')}"
                )
                return None
        return result
    
    def update_decision(
        self, decision_id: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing decision record in Zoho CRM.
        
        Args:
            decision_id: Zoho record ID (not our internal ID)
            update_data: Updated decision data
            
        Returns:
            Zoho API response, or None if failed
        """
        payload = {"data": [update_data]}
        result = self._make_request("PUT", f"Decisions/{decision_id}", payload)
        
        if result and result.get("data"):
            record = result["data"][0]
            # Success if code is 0 or message indicates update success
            if record.get("code") == 0 or "updated" in record.get("message", "").lower():
                logger.info(
                    f"✅ Updated Zoho decision record for team {self.team_id}: "
                    f"{decision_id} | {record.get('message')}"
                )
                return record
            else:
                logger.error(
                    f"❌ Zoho API error for team {self.team_id}: "
                    f"{record.get('message')}"
                )
                return None
        return result
    
    def get_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a decision record from Zoho CRM by Zoho record ID.
        
        Args:
            decision_id: Zoho record ID
            
        Returns:
            Decision record data, or None if not found
        """
        result = self._make_request("GET", f"Decisions/{decision_id}")
        
        if result and result.get("data"):
            return result["data"][0]
        return None
    
    def search_decision_by_id(self, decision_id: int) -> Optional[Dict[str, Any]]:
        """
        Search for a decision record by our internal Decision_Id.
        
        Since we include the Decision ID in the Name field (e.g., "Decision #14: ..."),
        we can search by fetching records and matching on the ID.
        
        Args:
            decision_id: Our internal decision ID
            
        Returns:
            Zoho decision record, or None if not found
        """
        # Fetch Decisions with essential fields
        result = self._make_request("GET", "Decisions?fields=id,Name,Decision_Id")
        
        if result and result.get("data"):
            for record in result["data"]:
                # Check if this matches our decision ID
                # Either by Decision_Id field or by extracting from Name
                if record.get("Decision_Id") == decision_id:
                    return record
                # Fallback: extract from Name (e.g., "Decision #14: ...")
                name = record.get("Name", "")
                if name.startswith(f"Decision #{decision_id}:"):
                    return record
        
        return None
    
    def test_connection(self) -> bool:
        """
        Test if API connection is working for this team.
        
        Returns:
            True if connection successful, False otherwise
        """
        logger.info(f"Testing Zoho CRM API connection for team {self.team_id}...")
        access_token = self.get_access_token()
        if not access_token:
            logger.error(f"❌ Could not obtain access token for team {self.team_id}")
            return False
        
        # Test with a simple request that lists decisions
        url = f"{self.api_domain}/crm/v3/Decisions?fields=id"
        headers = {
            "Authorization": f"Zoho-oauthtoken {access_token}",
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            # 200 = success with data, 204 = success with no data
            if response.status_code in [200, 204]:
                logger.info(
                    f"✅ Zoho CRM API connection successful for team {self.team_id}"
                )
                return True
            else:
                logger.error(
                    f"❌ Zoho CRM API returned status {response.status_code} "
                    f"for team {self.team_id}: {response.text}"
                )
                return False
        except Exception as e:
            logger.error(
                f"❌ Zoho CRM API connection failed for team {self.team_id}: {e}"
            )
            return False


# Note: No global client instance anymore!
# Each team gets their own client instance when needed.
