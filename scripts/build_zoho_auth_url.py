"""
Small helper to build a Zoho OAuth authorization URL.
Edit `CLIENT_ID` and `REDIRECT_URI` at the top, then run this script.
"""
import urllib.parse

# --- Edit these values before running ---
CLIENT_ID = "1000.W9DO0MRWSIBM9W9FS4OE8YB8WDV9GY"
# Example values you might use during development:
# REDIRECT_URI = "https://grandiose-nonlyric-hank.ngrok-free.dev/oauth/zoho/callback"
# or
REDIRECT_URI = "http://localhost:8000/oauth/zoho/callback"
# REDIRECT_URI = "https://grandiose-nonlyric-hank.ngrok-free.dev/oauth/zoho/callback"
ACCOUNTS_DOMAIN = "https://accounts.zoho.com"  # change to .eu/.in if your org is in that data center

params = {
    "scope": "ZohoCRM.modules.ALL",
    "client_id": CLIENT_ID,
    "response_type": "code",
    "access_type": "offline",
    "redirect_uri": REDIRECT_URI,
}

def build_auth_url(accounts_domain: str, params: dict) -> str:
    # URL-encode the redirect_uri properly
    encoded = {k: urllib.parse.quote(v, safe='') for k, v in params.items()}
    qs = "&".join(f"{k}={v}" for k, v in encoded.items())
    return f"{accounts_domain}/oauth/v2/auth?{qs}"

if __name__ == "__main__":
    if CLIENT_ID == "YOUR_CLIENT_ID_HERE":
        print("WARNING: Please set CLIENT_ID in this file before running.")

    print("Registered redirect URI to use:")
    print(f"  {REDIRECT_URI}\n")

    auth_url = build_auth_url(ACCOUNTS_DOMAIN, params)
    print("Copy & open this auth URL in your browser to start OAuth flow:")
    print(auth_url)
    print("\n(If you see 'invalid redirect url', ensure the redirect URI above exactly matches the one in Zoho console.)")
