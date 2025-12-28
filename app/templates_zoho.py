"""
HTML templates for Slack app pages.

These are served for OAuth success, privacy policy, and support pages.
"""

# =============================================================================
# ZOHO OAUTH ERROR PAGE
# =============================================================================

ZOHO_ERROR_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connection Failed - Decision Agent</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .container {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 500px;
            width: 100%;
            padding: 48px 32px;
            text-align: center;
            animation: slideUp 0.5s ease-out;
        }}
        
        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .error-icon {{
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
            animation: shake 0.5s ease-out;
        }}
        
        @keyframes shake {{
            0%, 100% {{ transform: translateX(0); }}
            25% {{ transform: translateX(-10px); }}
            75% {{ transform: translateX(10px); }}
        }}
        
        .error-icon svg {{
            width: 48px;
            height: 48px;
            stroke: white;
            fill: none;
            stroke-width: 3;
            stroke-linecap: round;
            stroke-linejoin: round;
        }}
        
        h1 {{
            color: #1a202c;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 16px;
        }}
        
        .subtitle {{
            color: #4a5568;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 32px;
        }}
        
        .error-box {{
            background: #fff5f5;
            border-left: 4px solid #f5576c;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 24px;
            text-align: left;
        }}
        
        .error-label {{
            color: #c53030;
            font-size: 12px;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .error-message {{
            color: #1a202c;
            font-size: 14px;
            line-height: 1.5;
            font-family: monospace;
            background: #f7fafc;
            padding: 12px;
            border-radius: 4px;
        }}
        
        .help-box {{
            background: #f7fafc;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 24px;
            text-align: left;
        }}
        
        .help-title {{
            color: #2d3748;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 12px;
        }}
        
        .help-item {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 12px;
        }}
        
        .help-item:last-child {{
            margin-bottom: 0;
        }}
        
        .help-number {{
            background: #e2e8f0;
            color: #2d3748;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: 600;
            margin-right: 12px;
            flex-shrink: 0;
        }}
        
        .help-text {{
            color: #4a5568;
            font-size: 14px;
            line-height: 1.5;
        }}
        
        .btn-group {{
            display: flex;
            gap: 12px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        .btn {{
            display: inline-block;
            padding: 14px 24px;
            font-size: 16px;
            font-weight: 600;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(245, 87, 108, 0.3);
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(245, 87, 108, 0.4);
        }}
        
        .btn-secondary {{
            background: #e2e8f0;
            color: #2d3748;
        }}
        
        .btn-secondary:hover {{
            background: #cbd5e0;
        }}
        
        .footer {{
            margin-top: 32px;
            padding-top: 24px;
            border-top: 1px solid #e2e8f0;
            color: #718096;
            font-size: 14px;
        }}
        
        .footer a {{
            color: #f5576c;
            text-decoration: none;
            font-weight: 600;
        }}
        
        .footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="error-icon">
            <svg viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="10"/>
                <line x1="15" y1="9" x2="9" y2="15"/>
                <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
        </div>
        
        <h1>❌ Connection Failed</h1>
        
        <p class="subtitle">
            We couldn't connect to your Zoho CRM account. Don't worry, let's fix this together.
        </p>
        
        <div class="error-box">
            <div class="error-label">Error Details</div>
            <div class="error-message">{error_message}</div>
        </div>
        
        <div class="help-box">
            <div class="help-title">💡 Troubleshooting Steps:</div>
            
            <div class="help-item">
                <span class="help-number">1</span>
                <div class="help-text">
                    Make sure you clicked "Authorize" in the Zoho CRM window
                </div>
            </div>
            
            <div class="help-item">
                <span class="help-number">2</span>
                <div class="help-text">
                    Check that you have admin access to your Zoho CRM account
                </div>
            </div>
            
            <div class="help-item">
                <span class="help-number">3</span>
                <div class="help-text">
                    Try the connection again - temporary network issues can cause failures
                </div>
            </div>
        </div>
        
        <div class="btn-group">
            <a href="{retry_url}" class="btn btn-primary">Try Again</a>
            <a href="/support" class="btn btn-secondary">Get Support</a>
        </div>
        
        <div class="footer">
            Still having issues? <a href="mailto:support@example.com">Contact Support</a>
        </div>
    </div>
</body>
</html>
"""

# =============================================================================
# ZOHO OAUTH SUCCESS PAGE - Closes popup and signals parent
# =============================================================================

ZOHO_OAUTH_SUCCESS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Connection Successful - Decision Agent</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .container {{
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 450px;
            width: 100%;
            padding: 48px 32px;
            text-align: center;
            animation: fadeIn 0.3s ease-out;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: scale(0.95); }}
            to {{ opacity: 1; transform: scale(1); }}
        }}
        
        .success-icon {{
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
            animation: checkPop 0.5s ease-out 0.2s both;
        }}
        
        @keyframes checkPop {{
            0% {{ transform: scale(0); }}
            50% {{ transform: scale(1.2); }}
            100% {{ transform: scale(1); }}
        }}
        
        .success-icon span {{
            font-size: 40px;
        }}
        
        h1 {{
            color: #1a202c;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 12px;
        }}
        
        .subtitle {{
            color: #4a5568;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 24px;
        }}
        
        .spinner {{
            width: 24px;
            height: 24px;
            border: 3px solid #e2e8f0;
            border-top-color: #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 8px;
            vertical-align: middle;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .closing-text {{
            color: #718096;
            font-size: 14px;
        }}
        
        .manual-close {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            display: none;
        }}
        
        .manual-close.show {{
            display: block;
        }}
        
        .btn {{
            display: inline-block;
            padding: 12px 28px;
            font-size: 15px;
            font-weight: 600;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">
            <span>✓</span>
        </div>
        
        <h1>🎉 Connection Successful!</h1>
        
        <p class="subtitle">
            {service_name} has been connected successfully.<br>
            Organization ID: <strong>{org_id}</strong>
        </p>
        
        <p class="closing-text">
            <span class="spinner"></span>
            Returning to dashboard...
        </p>
        
        <div class="manual-close" id="manualClose">
            <p style="color: #718096; font-size: 14px; margin-bottom: 12px;">
                Window didn't close automatically?
            </p>
            <button class="btn btn-primary" onclick="window.close()">Close This Window</button>
        </div>
    </div>
    
    <script>
        (function() {{
            var orgId = "{org_id}";
            var service = "{service_type}";
            
            // Try to notify the opener window (parent that opened this popup)
            function notifyParent() {{
                try {{
                    // Method 1: postMessage to opener
                    if (window.opener) {{
                        window.opener.postMessage({{
                            type: 'oauth_success',
                            service: service,
                            org_id: orgId
                        }}, '*');
                        console.log('Sent postMessage to opener');
                    }}
                    
                    // Method 2: Try to refresh opener location directly
                    if (window.opener && !window.opener.closed) {{
                        try {{
                            // Set a flag in localStorage that the dashboard can read
                            localStorage.setItem('oauth_complete', JSON.stringify({{
                                service: service,
                                org_id: orgId,
                                timestamp: Date.now()
                            }}));
                        }} catch(e) {{
                            console.log('localStorage not available');
                        }}
                    }}
                }} catch(e) {{
                    console.log('Could not notify parent:', e);
                }}
            }}
            
            // Notify parent immediately
            notifyParent();
            
            // Try to close this window after a short delay
            setTimeout(function() {{
                try {{
                    window.close();
                }} catch(e) {{
                    console.log('Could not close window');
                }}
                
                // If window didn't close, show manual close button
                setTimeout(function() {{
                    document.getElementById('manualClose').classList.add('show');
                }}, 500);
            }}, 1500);
        }})();
    </script>
</body>
</html>
"""

# =============================================================================
# ZOHO DASHBOARD PAGE
# =============================================================================

ZOHO_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Integrations Dashboard - Decision Agent</title>
    
    <!-- Zoho CRM Client Script SDK for WebTab integration -->
    <script src="https://live.zwidgets.com/js-sdk/1.2/ZohoEmbededAppSDK.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f7fafc;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .header {{
            max-width: 800px;
            margin: 0 auto 32px;
            text-align: center;
        }}
        
        .logo {{
            font-size: 36px;
            margin-bottom: 8px;
        }}
        
        h1 {{
            color: #1a202c;
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        
        .team-name {{
            color: #4a5568;
            font-size: 18px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .card {{
            background: white;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            padding: 32px;
            margin-bottom: 24px;
            transition: all 0.3s ease;
        }}
        
        .card:hover {{
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        
        .card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 2px solid #e2e8f0;
        }}
        
        .card-title {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .card-icon {{
            font-size: 32px;
        }}
        
        .card-title-text {{
            color: #1a202c;
            font-size: 24px;
            font-weight: 700;
        }}
        
        .status-badge {{
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .status-connected {{
            background: #c6f6d5;
            color: #22543d;
        }}
        
        .status-disconnected {{
            background: #fed7d7;
            color: #742a2a;
        }}
        
        .card-body {{
            color: #4a5568;
            line-height: 1.6;
        }}
        
        .info-grid {{
            display: grid;
            gap: 16px;
            margin: 20px 0;
        }}
        
        .info-item {{
            display: flex;
            justify-content: space-between;
            padding: 12px;
            background: #f7fafc;
            border-radius: 8px;
        }}
        
        .info-label {{
            color: #718096;
            font-size: 14px;
        }}
        
        .info-value {{
            color: #1a202c;
            font-weight: 600;
            font-size: 14px;
        }}
        
        .btn {{
            display: inline-block;
            padding: 12px 28px;
            font-size: 15px;
            font-weight: 600;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
            text-align: center;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-danger {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(245, 87, 108, 0.3);
        }}
        
        .btn-danger:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(245, 87, 108, 0.4);
        }}
        
        .btn-disabled {{
            background: #e2e8f0;
            color: #a0aec0;
            cursor: not-allowed;
        }}
        
        .btn-disabled:hover {{
            transform: none;
            box-shadow: none;
        }}
        
        .alert {{
            padding: 16px 20px;
            border-radius: 8px;
            margin-bottom: 24px;
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }}
        
        .alert-info {{
            background: #ebf8ff;
            border-left: 4px solid #3182ce;
            color: #2c5282;
        }}
        
        .alert-warning {{
            background: #fffaf0;
            border-left: 4px solid #ed8936;
            color: #7c2d12;
        }}
        
        .alert-icon {{
            font-size: 20px;
            flex-shrink: 0;
        }}
        
        .footer {{
            max-width: 800px;
            margin: 48px auto 0;
            text-align: center;
            color: #718096;
            font-size: 14px;
            padding-top: 24px;
            border-top: 1px solid #e2e8f0;
        }}
        
        .footer a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}
        
        .footer a:hover {{
            text-decoration: underline;
        }}
        
        /* Success Message Cards - Minimal Style */
        .success-card {{
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 16px;
            border: 1px solid #e2e8f0;
        }}
        
        .success-card-slack {{
            background: #f8fafc;
            border-left: 3px solid #667eea;
        }}
        
        .success-card-zoho {{
            background: #f8fafc;
            border-left: 3px solid #38a169;
        }}
        
        .success-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
        }}
        
        .success-icon {{
            font-size: 20px;
        }}
        
        .success-title {{
            font-size: 15px;
            font-weight: 600;
            color: #2d3748;
        }}
        
        .success-subtitle {{
            font-size: 13px;
            color: #718096;
            margin-bottom: 12px;
        }}
        
        .success-commands {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 12px;
        }}
        
        .success-commands-title {{
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 8px;
            color: #4a5568;
        }}
        
        .command-item {{
            background: #f7fafc;
            padding: 6px 10px;
            border-radius: 4px;
            font-family: 'SF Mono', 'Consolas', monospace;
            font-size: 12px;
            margin-bottom: 4px;
            color: #4a5568;
        }}
        
        .command-item:last-child {{
            margin-bottom: 0;
        }}
        
        .success-features {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 12px;
        }}
        
        .success-feature {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
            font-size: 13px;
            color: #4a5568;
        }}
        
        .success-feature:last-child {{
            margin-bottom: 0;
        }}
        
        .success-feature-icon {{
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">📊</div>
        <h1>Integrations Dashboard</h1>
        <p class="team-name">{team_name}</p>
    </div>
    
    <div class="container">
        <!-- Debug Panel (collapsible) -->
        <details style="margin-bottom: 20px; background: #1a202c; border-radius: 8px; padding: 12px; color: #e2e8f0;" open>
            <summary style="cursor: pointer; font-weight: 600; color: #68d391;">🔧 Debug Info (click to expand)</summary>
            <div style="margin-top: 12px; font-family: monospace; font-size: 12px; line-height: 1.6;">
                <div><strong>Current Org ID:</strong> <span id="debug-org-id">{team_id}</span></div>
                <div><strong>URL Params:</strong> <span id="debug-url-params">Loading...</span></div>
                <div><strong>Zoho SDK Status:</strong> <span id="debug-sdk-status">Checking...</span></div>
                <div><strong>Zoho Org (from SDK):</strong> <span id="debug-zoho-org">Not fetched yet</span></div>
                <div style="margin-top: 12px;">
                    <button onclick="checkApiStatus()" style="background: #4299e1; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 12px;">🔍 Check API Status</button>
                </div>
                <div style="margin-top: 8px;"><strong>API Response:</strong></div>
                <div id="debug-api-response" style="background: #2d3748; padding: 8px; border-radius: 4px; margin-top: 4px; white-space: pre-wrap;">Click button above to check</div>
                <div style="margin-top: 8px;"><strong>Log:</strong></div>
                <div id="debug-log" style="background: #2d3748; padding: 8px; border-radius: 4px; max-height: 150px; overflow-y: auto; margin-top: 4px;"></div>
            </div>
        </details>
        
        {alert_html}
        
        <!-- Zoho CRM Integration Card (FIRST - Primary Connection) -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <span class="card-icon">🔗</span>
                    <span class="card-title-text">Zoho CRM</span>
                </div>
                <span class="status-badge {zoho_status_class}">{zoho_status_text}</span>
            </div>
            <div class="card-body">
                <p>{zoho_description}</p>
                
                {zoho_info_html}
                
                <div style="margin-top: 24px;">
                    {zoho_action_button}
                </div>
            </div>
        </div>
        
        <!-- Zoho Success Message (shown when connected) -->
        {zoho_success_html}
        
        <!-- Slack Integration Card (SECOND - Requires Zoho) -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <span class="card-icon">💬</span>
                    <span class="card-title-text">Slack</span>
                </div>
                <span class="status-badge {slack_status_class}">{slack_status_text}</span>
            </div>
            <div class="card-body">
                <p>{slack_description}</p>
                
                {slack_info_html}
                
                <div style="margin-top: 24px;">
                    {slack_action_button}
                </div>
            </div>
        </div>
        
        <!-- Slack Success Message (shown when connected) -->
        {slack_success_html}
    </div>
    
    <div class="footer">
        Need help? <a href="/support">Contact Support</a> | 
        <a href="/privacy">Privacy Policy</a>
    </div>
    <script>
        (function() {{
            var currentOrgId = "{team_id}";
            var isZohoInitialized = false;
            
            // ================================================================
            // DEBUG LOGGING
            // ================================================================
            
            function debugLog(msg) {{
                console.log(msg);
                var logDiv = document.getElementById('debug-log');
                if (logDiv) {{
                    var time = new Date().toLocaleTimeString();
                    logDiv.innerHTML += '<div style="color: #a0aec0;">[' + time + '] ' + msg + '</div>';
                    logDiv.scrollTop = logDiv.scrollHeight;
                }}
            }}
            
            function updateDebugInfo() {{
                // URL params
                var urlParamsDiv = document.getElementById('debug-url-params');
                if (urlParamsDiv) {{
                    urlParamsDiv.textContent = window.location.search || '(none)';
                }}
            }}
            updateDebugInfo();
            
            // Make checkApiStatus available globally
            window.checkApiStatus = function() {{
                var apiResponseDiv = document.getElementById('debug-api-response');
                var orgId = currentOrgId || 'N/A';
                
                if (orgId === 'N/A' || !orgId) {{
                    if (apiResponseDiv) apiResponseDiv.textContent = '❌ No org_id available to check';
                    return;
                }}
                
                if (apiResponseDiv) apiResponseDiv.textContent = '🔄 Checking...';
                debugLog('🔍 Calling /zoho/status?org_id=' + orgId);
                
                fetch('/zoho/status?org_id=' + orgId)
                    .then(function(response) {{
                        return response.json();
                    }})
                    .then(function(data) {{
                        debugLog('✅ API Response received');
                        if (apiResponseDiv) {{
                            apiResponseDiv.textContent = JSON.stringify(data, null, 2);
                        }}
                        
                        // If connected, show a success message
                        if (data.connected) {{
                            debugLog('✅ Backend says CONNECTED!');
                        }} else {{
                            debugLog('❌ Backend says NOT CONNECTED: ' + data.message);
                        }}
                    }})
                    .catch(function(err) {{
                        debugLog('❌ API Error: ' + err);
                        if (apiResponseDiv) apiResponseDiv.textContent = '❌ Error: ' + err;
                    }});
            }};
            
            // Auto-check API status on page load if we have an org_id
            if (currentOrgId && currentOrgId !== 'N/A') {{
                setTimeout(window.checkApiStatus, 1000);
            }}
            
            // ================================================================
            // ZOHO OAUTH FLOW WITH ORG_ID VALIDATION
            // ================================================================
            
            // Store the org_id fetched from SDK (will be populated by SDK init)
            var sdkOrgId = null;
            
            window.startZohoOAuth = function() {{
                debugLog('🔐 Starting Zoho OAuth flow...');
                
                // First, try to use the org_id we already have from the URL/SDK
                // This is the most reliable as it's already validated
                if (sdkOrgId) {{
                    debugLog('✅ Using cached SDK org_id: ' + sdkOrgId);
                    openOAuthWindow(sdkOrgId);
                    return;
                }}
                
                // Fallback to currentOrgId from URL if available
                if (currentOrgId && currentOrgId !== 'N/A' && currentOrgId !== '') {{
                    debugLog('✅ Using org_id from URL: ' + currentOrgId);
                    openOAuthWindow(currentOrgId);
                    return;
                }}
                
                // Last resort: try to fetch from SDK with a timeout
                if (typeof ZOHO !== 'undefined' && ZOHO.CRM && ZOHO.CRM.CONFIG) {{
                    debugLog('🔄 Fetching org_id from SDK (3s timeout)...');
                    
                    var timeoutId = null;
                    var resolved = false;
                    
                    // Create a timeout to avoid hanging forever
                    timeoutId = setTimeout(function() {{
                        if (!resolved) {{
                            resolved = true;
                            debugLog('⏱️ SDK timeout - proceeding without org_id validation');
                            openOAuthWindow(null);
                        }}
                    }}, 3000); // 3 second timeout
                    
                    ZOHO.CRM.CONFIG.getOrgInfo().then(function(response) {{
                        if (resolved) return; // Already timed out
                        resolved = true;
                        clearTimeout(timeoutId);
                        
                        if (response && response.org && response.org.length > 0) {{
                            sdkOrgId = response.org[0].zgid;
                            debugLog('✅ Got org_id from SDK: ' + sdkOrgId);
                            openOAuthWindow(sdkOrgId);
                        }} else {{
                            debugLog('⚠️ No org_id from SDK, proceeding without validation');
                            openOAuthWindow(null);
                        }}
                    }}).catch(function(err) {{
                        if (resolved) return; // Already timed out
                        resolved = true;
                        clearTimeout(timeoutId);
                        
                        debugLog('❌ Error fetching org_id: ' + err);
                        openOAuthWindow(null);
                    }});
                }} else {{
                    // SDK not available - might be running outside Zoho context
                    debugLog('⚠️ SDK not available, proceeding without org_id validation');
                    openOAuthWindow(null);
                }}
            }};
            
            function openOAuthWindow(expectedOrgId) {{
                var url = '/zoho/install';
                if (expectedOrgId) {{
                    url += '?expected_org_id=' + expectedOrgId;
                }}
                debugLog('🔗 Opening OAuth URL: ' + url);
                window.open(url, '_blank');
            }}
            
            // ================================================================
            // ZOHO CRM SDK INITIALIZATION
            // ================================================================
            
            function initZohoSDK() {{
                var sdkStatus = document.getElementById('debug-sdk-status');
                
                if (typeof ZOHO === 'undefined') {{
                    debugLog('❌ ZOHO global object not found');
                    if (sdkStatus) sdkStatus.textContent = '❌ SDK not loaded';
                    return;
                }}
                
                if (!ZOHO.embeddedApp) {{
                    debugLog('❌ ZOHO.embeddedApp not available');
                    if (sdkStatus) sdkStatus.textContent = '❌ embeddedApp not available';
                    return;
                }}
                
                debugLog('🔄 Initializing Zoho SDK...');
                if (sdkStatus) sdkStatus.textContent = '🔄 Initializing...';
                
                try {{
                    // Initialize the embedded app
                    ZOHO.embeddedApp.on("PageLoad", function(data) {{
                        debugLog('✅ PageLoad event received');
                        debugLog('PageLoad data: ' + JSON.stringify(data));
                        isZohoInitialized = true;
                        if (sdkStatus) sdkStatus.textContent = '✅ PageLoad received';
                        
                        // Try to get org info from Zoho CRM context
                        fetchZohoOrgId();
                    }});
                    
                    ZOHO.embeddedApp.init().then(function() {{
                        debugLog('✅ embeddedApp.init() successful');
                    }}).catch(function(err) {{
                        debugLog('❌ embeddedApp.init() error: ' + err);
                        if (sdkStatus) sdkStatus.textContent = '❌ Init failed';
                    }});
                    
                }} catch(e) {{
                    debugLog('❌ Exception in initZohoSDK: ' + e);
                    if (sdkStatus) sdkStatus.textContent = '❌ Exception';
                }}
            }}
            
            function fetchZohoOrgId() {{
                var zohoOrgDiv = document.getElementById('debug-zoho-org');
                
                if (typeof ZOHO === 'undefined' || !ZOHO.CRM) {{
                    debugLog('❌ ZOHO.CRM not available');
                    if (zohoOrgDiv) zohoOrgDiv.textContent = '❌ CRM API not available';
                    return;
                }}
                
                debugLog('🔄 Fetching org info via ZOHO.CRM.CONFIG.getOrgInfo()...');
                
                // Get organization info from Zoho CRM
                ZOHO.CRM.CONFIG.getOrgInfo().then(function(response) {{
                    debugLog('✅ getOrgInfo response: ' + JSON.stringify(response));
                    
                    if (response && response.org && response.org.length > 0) {{
                        var zohoOrgId = response.org[0].zgid;
                        sdkOrgId = zohoOrgId; // Store for OAuth flow
                        debugLog('✅ Zoho Org ID (zgid): ' + zohoOrgId);
                        if (zohoOrgDiv) zohoOrgDiv.textContent = zohoOrgId;
                        
                        // If current page doesn't have the org_id or has wrong one, reload with correct org_id
                        if (zohoOrgId && (currentOrgId === 'N/A' || !currentOrgId || currentOrgId !== zohoOrgId)) {{
                            debugLog('🔄 Reloading with correct org_id: ' + zohoOrgId);
                            window.location.href = '/dashboard?orgId=' + zohoOrgId;
                        }} else {{
                            debugLog('✅ Org ID matches, no reload needed');
                        }}
                    }} else {{
                        debugLog('⚠️ No org data in response');
                        if (zohoOrgDiv) zohoOrgDiv.textContent = '⚠️ No org data';
                    }}
                }}).catch(function(err) {{
                    debugLog('❌ getOrgInfo error: ' + err);
                    if (zohoOrgDiv) zohoOrgDiv.textContent = '❌ Error: ' + err;
                }});
            }}
            
            // Initialize Zoho SDK on page load
            if (document.readyState === 'complete') {{
                initZohoSDK();
            }} else {{
                window.addEventListener('load', initZohoSDK);
            }}
            
            // ================================================================
            // OAUTH POPUP COMMUNICATION (fallback methods)
            // ================================================================
            
            // Listen for postMessage from OAuth popup
            window.addEventListener('message', function(event) {{
                try {{
                    var data = event.data;
                    if (data && data.type === 'oauth_success') {{
                        console.log('Received OAuth success message:', data);
                        // Refresh the page with the org_id
                        var orgId = data.org_id || currentOrgId;
                        if (orgId && orgId !== 'N/A') {{
                            window.location.href = '/dashboard?org_id=' + orgId;
                        }} else {{
                            window.location.reload();
                        }}
                    }}
                }} catch(e) {{
                    console.log('Error processing message:', e);
                }}
            }});
            
            // Check localStorage for OAuth completion on page load
            function checkLocalStorageForOAuth() {{
                try {{
                    var oauthData = localStorage.getItem('oauth_complete');
                    if (oauthData) {{
                        var data = JSON.parse(oauthData);
                        // Only process if it's recent (within last 30 seconds)
                        if (Date.now() - data.timestamp < 30000) {{
                            console.log('Found recent OAuth completion:', data);
                            // Clear the flag
                            localStorage.removeItem('oauth_complete');
                            // Refresh with the new org_id
                            if (data.org_id) {{
                                window.location.href = '/dashboard?org_id=' + data.org_id;
                            }} else {{
                                window.location.reload();
                            }}
                        }} else {{
                            // Clear old flag
                            localStorage.removeItem('oauth_complete');
                        }}
                    }}
                }} catch(e) {{
                    console.log('localStorage check error:', e);
                }}
            }}
            
            // Check immediately on page load
            checkLocalStorageForOAuth();
            
            // Also poll localStorage every 2 seconds (for cross-tab communication)
            setInterval(checkLocalStorageForOAuth, 2000);
            
            // Focus handler - check when window regains focus (user closes popup and comes back)
            window.addEventListener('focus', function() {{
                // Small delay to let localStorage update
                setTimeout(checkLocalStorageForOAuth, 500);
                
                // Also try to refetch from Zoho SDK if available
                if (isZohoInitialized) {{
                    setTimeout(fetchZohoOrgId, 1000);
                }}
            }});
        }})();
    </script>
</body>
</html>
"""
