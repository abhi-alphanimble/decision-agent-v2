"""
Zoho CRM OAuth callback handler.
"""
import logging
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/oauth/zoho/callback")
async def zoho_oauth_callback(request: Request):
    """
    Zoho OAuth callback endpoint.
    Captures the authorization code and displays it for the user to save.
    """
    # Extract query parameters
    code = request.query_params.get("code")
    error = request.query_params.get("error")
    error_description = request.query_params.get("error_description")
    location = request.query_params.get("location", "unknown")
    accounts_server = request.query_params.get("accounts-server", "unknown")

    logger.info(
        f"Zoho OAuth callback received | location={location} | accounts_server={accounts_server}"
    )

    if error:
        logger.error(f"OAuth error: {error} - {error_description}")
        return HTMLResponse(
            f"""
            <html>
            <head><title>Zoho OAuth Error</title></head>
            <body style="font-family: Arial; padding: 20px;">
                <h1>❌ Zoho OAuth Error</h1>
                <p><strong>Error Code:</strong> {error}</p>
                <p><strong>Description:</strong> {error_description}</p>
                <p><a href="/">Back to home</a></p>
            </body>
            </html>
            """,
            status_code=400,
        )

    if not code:
        logger.error("OAuth callback received but no authorization code present")
        return HTMLResponse(
            """
            <html>
            <head><title>Zoho OAuth Error</title></head>
            <body style="font-family: Arial; padding: 20px;">
                <h1>❌ Missing Authorization Code</h1>
                <p>No authorization code received from Zoho. Please try again.</p>
                <p><a href="/">Back to home</a></p>
            </body>
            </html>
            """,
            status_code=400,
        )

    logger.info(f"✅ Authorization code received: {code[:20]}...")

    # Display the code to the user for copying
    return HTMLResponse(
        f"""
        <html>
        <head>
            <title>Zoho OAuth Success</title>
            <style>
                body {{ font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
                .code-box {{ background: #f0f0f0; padding: 15px; border-radius: 4px; word-break: break-all; margin: 15px 0; font-family: monospace; }}
                .success {{ color: #28a745; font-weight: bold; }}
                button {{ padding: 10px 15px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; }}
                button:hover {{ background: #0056b3; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✅ <span class="success">Zoho OAuth Success!</span></h1>
                <p>Your authorization code has been received. Copy it below and use it in the token exchange step.</p>
                
                <h3>Authorization Code:</h3>
                <div class="code-box" id="codeBox">{code}</div>
                <button onclick="copyCode()">📋 Copy Code</button>
                
                <h3>Next Steps:</h3>
                <ol>
                    <li>Copy the authorization code above</li>
                    <li>Run the PowerShell command in your terminal to exchange it for tokens</li>
                    <li>Save the <code>refresh_token</code> to your <code>.env</code> file</li>
                </ol>
                
                <p><strong>Location:</strong> {location}</p>
                <p><strong>Accounts Server:</strong> {accounts_server}</p>
                
                <p><a href="/">Back to home</a></p>
            </div>
            
            <script>
                function copyCode() {{
                    const codeBox = document.getElementById("codeBox");
                    const text = codeBox.innerText;
                    navigator.clipboard.writeText(text).then(() => {{
                        alert("Code copied to clipboard!");
                    }}).catch(() => {{
                        alert("Failed to copy. Please copy manually.");
                    }});
                }}
            </script>
        </body>
        </html>
        """
    )
