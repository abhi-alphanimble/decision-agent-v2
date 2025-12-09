"""
Zoho CRM API client for Decision Agent integration.
Handles OAuth token management and API requests.
"""
import logging
import os
from datetime import datetime, timedelta
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ZohoCRMClient:
    """Client for Zoho CRM API with OAuth 2.0 support"""

    def __init__(self):
        self.client_id = os.getenv("ZOHO_CLIENT_ID")
        self.client_secret = os.getenv("ZOHO_CLIENT_SECRET")
        self.refresh_token = os.getenv("ZOHO_REFRESH_TOKEN")
        self.api_domain = os.getenv("ZOHO_API_DOMAIN", "https://www.zohoapis.in")
        self.accounts_url = os.getenv("ZOHO_ACCOUNTS_URL", "https://accounts.zoho.in")
        
        self.access_token: Optional[str] = None
        self.token_expiry: Optional[datetime] = None
        
        if not all([self.client_id, self.client_secret, self.refresh_token]):
            logger.warning("Zoho credentials not fully configured in environment")
    
    def get_access_token(self) -> Optional[str]:
        """
        Get a valid access token, refreshing if necessary.
        Returns None if credentials are not configured.
        """
        if not self.client_id or not self.client_secret or not self.refresh_token:
            logger.error("Zoho credentials not configured")
            return None
        
        # Check if token is still valid (with 5-minute buffer)
        if self.access_token and self.token_expiry:
            if datetime.utcnow() < (self.token_expiry - timedelta(minutes=5)):
                logger.debug("Using cached access token")
                return self.access_token
        
        # Refresh the token
        try:
            logger.info("Refreshing Zoho access token...")
            response = requests.post(
                f"{self.accounts_url}/oauth/v2/token",
                data={
                    "refresh_token": self.refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "refresh_token",
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                expires_in = data.get("expires_in", 3600)  # Default 1 hour
                self.token_expiry = datetime.utcnow() + timedelta(seconds=expires_in)
                logger.info(f"✅ Zoho access token refreshed (expires in {expires_in}s)")
                return self.access_token
            else:
                logger.error(f"❌ Failed to refresh token: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"❌ Error refreshing token: {e}", exc_info=True)
            return None
    
    def _make_request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Make an authenticated request to Zoho CRM API"""
        access_token = self.get_access_token()
        if not access_token:
            logger.error("Could not obtain access token for API request")
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
                    f"API request failed: {method} {endpoint} - "
                    f"{response.status_code}: {response.text}"
                )
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}", exc_info=True)
            return None
    
    def create_decision(self, decision_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new decision record in Zoho CRM"""
        # Wrap data in 'data' key as per Zoho API format
        payload = {"data": [decision_data]}
        result = self._make_request("POST", "Decisions", payload)
        
        if result and result.get("data"):
            record = result["data"][0]
            # Success if code is 0 or message is "record added"
            if record.get("code") == 0 or "added" in record.get("message", "").lower():
                logger.info(f"✅ Created Zoho decision record: {record.get('id')} | {record.get('message')}")
                return record
            else:
                logger.error(f"❌ Zoho API error: {record.get('message')}")
                return None
        return result
    
    def update_decision(
        self, decision_id: str, update_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update an existing decision record in Zoho CRM"""
        payload = {"data": [update_data]}
        result = self._make_request("PUT", f"Decisions/{decision_id}", payload)
        
        if result and result.get("data"):
            record = result["data"][0]
            # Success if code is 0 or message indicates update success
            if record.get("code") == 0 or "updated" in record.get("message", "").lower():
                logger.info(f"✅ Updated Zoho decision record: {decision_id} | {record.get('message')}")
                return record
            else:
                logger.error(f"❌ Zoho API error: {record.get('message')}")
                return None
        return result
    
    def get_decision(self, decision_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a decision record from Zoho CRM by Zoho record ID"""
        result = self._make_request("GET", f"Decisions/{decision_id}")
        
        if result and result.get("data"):
            return result["data"][0]
        return None
    
    def search_decision_by_id(self, decision_id: int) -> Optional[Dict[str, Any]]:
        """Search for a decision record by Decision_Id (our internal ID)
        
        Since we include the Decision ID in the Name field (e.g., "Decision #14: ..."),
        we can search locally by fetching records and matching on the ID.
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
        """Test if API connection is working"""
        logger.info("Testing Zoho CRM API connection...")
        access_token = self.get_access_token()
        if not access_token:
            logger.error("❌ Could not obtain access token")
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
                logger.info("✅ Zoho CRM API connection successful")
                return True
            else:
                logger.error(f"❌ Zoho CRM API returned status {response.status_code}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Zoho CRM API connection failed: {e}")
            return False


# Global client instance
zoho_client = ZohoCRMClient()
