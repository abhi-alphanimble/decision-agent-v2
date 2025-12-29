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
            Still having issues? <a href="mailto:support@decisionagent.ai">Contact Support</a>
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
# ZOHO DASHBOARD PAGE - NEW CLEAN DESIGN
# =============================================================================

ZOHO_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Integration Dashboard - Decision Agent</title>
    
    <!-- Zoho CRM Client Script SDK for WebTab integration -->
    <script src="https://live.zwidgets.com/js-sdk/1.2/ZohoEmbededAppSDK.min.js"></script>
    <style>
        :root {{
            --bg-body: #f1f5f9;
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --border: #e2e8f0;
            --radius: 12px;
            --danger: #ef4444;
            --danger-hover: #b91c1c;
            --success: #10b981;
            --success-bg: #dcfce7;
            --success-text: #166534;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.5;
            padding: 40px 20px;
        }}

        .container {{ max-width: 760px; margin: 0 auto; }}

        /* Header */
        .header {{ text-align: center; margin-bottom: 40px; }}
        .header h1 {{ font-size: 24px; font-weight: 700; margin-bottom: 8px; }}
        .header p {{ color: var(--text-muted); font-size: 15px; }}

        /* Alert */
        .alert-setup {{
            background: #eff6ff;
            border: 1px solid #dbeafe;
            color: #1e40af;
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 32px;
            display: flex;
            gap: 12px;
            align-items: center;
            font-size: 14px;
            font-weight: 500;
        }}

        /* Card System */
        .card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            margin-bottom: 24px;
            overflow: hidden;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}
        
        /* Top: Brand + Active Badge */
        .card-header {{
            padding: 24px 24px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .brand-section {{ display: flex; align-items: center; gap: 14px; }}
        .logo-box {{ width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; }}
        .logo-svg {{ width: 100%; height: 100%; }}
        
        .brand-title {{ font-size: 18px; font-weight: 700; color: var(--text-main); }}
        .brand-subtitle {{ font-size: 13px; color: var(--text-muted); }}

        /* Status Badges */
        .status-badge {{
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            background: #f1f5f9;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .badge-active {{
            background-color: var(--success-bg);
            color: var(--success-text);
            font-size: 12px;
            font-weight: 700;
            padding: 6px 12px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            gap: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Card Body for before connect */
        .card-body {{ padding: 32px 24px; text-align: center; }}
        .description {{ color: var(--text-muted); margin-bottom: 24px; max-width: 400px; margin-left: auto; margin-right: auto; }}

        /* Grid Layout for Details */
        .grid-container {{
            background: #f8fafc;
            margin: 0 24px;
            padding: 20px;
            border-radius: 8px;
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 24px;
            border: 1px solid #f1f5f9;
        }}

        .grid-item {{ display: flex; flex-direction: column; gap: 4px; }}
        
        .label {{
            font-size: 12px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }}
        
        .value {{
            font-size: 15px;
            font-weight: 600;
            color: var(--text-main);
            font-variant-numeric: tabular-nums;
        }}

        /* Footer: Date + Disconnect */
        .card-footer {{
            padding: 20px 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .date-meta {{
            font-size: 13px;
            color: var(--text-muted);
            font-weight: 500;
        }}

        /* Buttons */
        .btn {{
            display: inline-flex; 
            align-items: center; 
            gap: 8px;
            padding: 10px 24px; 
            border-radius: 8px;
            font-weight: 600; 
            font-size: 14px;
            cursor: pointer; 
            border: none; 
            transition: all 0.2s;
        }}

        .btn-primary {{ background: var(--primary); color: white; }}
        .btn-primary:hover {{ background: var(--primary-hover); transform: translateY(-1px); }}
        
        .btn-disabled {{ 
            background: #f1f5f9; 
            color: #94a3b8; 
            cursor: not-allowed; 
            border: 1px solid var(--border); 
        }}

        .btn-disconnect {{
            background: transparent;
            border: 1px solid var(--danger);
            color: var(--danger);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            padding: 8px 16px;
            border-radius: 6px;
            transition: all 0.2s;
        }}
        
        .btn-disconnect:hover {{
            background: #fef2f2;
            color: var(--danger-hover);
            border-color: var(--danger-hover);
        }}

        /* Locked State Overlay */
        .locked-card {{ opacity: 0.7; position: relative; }}
        .locked-card .card-body {{ filter: grayscale(100%); }}

        /* Quick Commands Section */
        .commands-card {{
            background: #ffffff;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 24px;
            margin-top: 32px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }}

        .commands-title {{
            font-size: 12px;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 16px;
        }}

        .command-row {{
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 12px 0;
            border-bottom: 1px solid #e2e8f0;
        }}
        .command-row:last-child {{ border-bottom: none; }}

        .cmd-pill {{
            background: #eff6ff;
            color: var(--primary);
            border: 1px solid #dbeafe;
            font-family: 'SF Mono', Consolas, monospace;
            font-size: 13px;
            font-weight: 600;
            padding: 6px 10px;
            border-radius: 6px;
            min-width: 80px;
            text-align: center;
        }}

        .cmd-desc {{ font-size: 14px; color: var(--text-main); }}

        /* Footer */
        .footer {{
            max-width: 760px;
            margin: 48px auto 0;
            text-align: center;
            color: var(--text-muted);
            font-size: 14px;
            padding-top: 24px;
            border-top: 1px solid var(--border);
        }}
        
        .footer a {{
            color: var(--primary);
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
        <div class="header">
            <h1>{header_title}</h1>
            <p>{header_subtitle}</p>
        </div>

        {alert_html}

        <!-- Zoho CRM Integration Card -->
        {zoho_card_html}

        <!-- Slack Integration Card -->
        {slack_card_html}

        <!-- Quick Commands (shown when both connected) -->
        {commands_html}
    </div>

    <div class="footer">
        Need help? <a href="/support?orgId={team_id}">Contact Support</a> | 
        <a href="/privacy?orgId={team_id}">Privacy Policy</a>
    </div>
    
    <script>
        (function() {{
            var currentOrgId = "{team_id}";
            var isZohoInitialized = false;
            var sdkOrgId = null;
            
            // ================================================================
            // ZOHO OAUTH FLOW
            // ================================================================
            
            window.startZohoOAuth = function() {{
                if (sdkOrgId) {{
                    openOAuthWindow(sdkOrgId);
                    return;
                }}
                
                if (currentOrgId && currentOrgId !== 'N/A' && currentOrgId !== '') {{
                    openOAuthWindow(currentOrgId);
                    return;
                }}
                
                if (typeof ZOHO !== 'undefined' && ZOHO.CRM && ZOHO.CRM.CONFIG) {{
                    var timeoutId = null;
                    var resolved = false;
                    
                    timeoutId = setTimeout(function() {{
                        if (!resolved) {{
                            resolved = true;
                            openOAuthWindow(null);
                        }}
                    }}, 3000);
                    
                    ZOHO.CRM.CONFIG.getOrgInfo().then(function(response) {{
                        if (resolved) return;
                        resolved = true;
                        clearTimeout(timeoutId);
                        
                        if (response && response.org && response.org.length > 0) {{
                            sdkOrgId = response.org[0].zgid;
                            openOAuthWindow(sdkOrgId);
                        }} else {{
                            openOAuthWindow(null);
                        }}
                    }}).catch(function(err) {{
                        if (resolved) return;
                        resolved = true;
                        clearTimeout(timeoutId);
                        openOAuthWindow(null);
                    }});
                }} else {{
                    openOAuthWindow(null);
                }}
            }};
            
            window.startSlackOAuth = function(orgId) {{
                var url = '/slack/install?org_id=' + orgId;
                window.open(url, 'SlackOAuth', 'width=600,height=800,status=no,resizable=yes,scrollbars=yes');
            }};
            
            function openOAuthWindow(expectedOrgId) {{
                var url = '/zoho/install';
                if (expectedOrgId) {{
                    url += '?expected_org_id=' + expectedOrgId;
                }}
                window.open(url, 'ZohoOAuth', 'width=800,height=700,status=no,resizable=yes,scrollbars=yes');
            }}
            
            // ================================================================
            // ZOHO CRM SDK INITIALIZATION
            // ================================================================
            
            function initZohoSDK() {{
                if (typeof ZOHO === 'undefined' || !ZOHO.embeddedApp) {{
                    return;
                }}
                
                try {{
                    ZOHO.embeddedApp.on("PageLoad", function(data) {{
                        isZohoInitialized = true;
                        fetchZohoOrgId();
                    }});
                    
                    ZOHO.embeddedApp.init().catch(function(err) {{
                        console.log('Zoho SDK init error:', err);
                    }});
                }} catch(e) {{
                    console.log('Error initializing Zoho SDK:', e);
                }}
            }}
            
            function fetchZohoOrgId() {{
                if (typeof ZOHO === 'undefined' || !ZOHO.CRM) {{
                    return;
                }}
                
                ZOHO.CRM.CONFIG.getOrgInfo().then(function(response) {{
                    if (response && response.org && response.org.length > 0) {{
                        var zohoOrgId = response.org[0].zgid;
                        sdkOrgId = zohoOrgId;
                        
                        if (zohoOrgId && (currentOrgId === 'N/A' || !currentOrgId || currentOrgId !== zohoOrgId)) {{
                            window.location.href = '/dashboard?orgId=' + zohoOrgId;
                        }}
                    }}
                }}).catch(function(err) {{
                    console.log('Error fetching Zoho org info:', err);
                }});
            }}
            
            if (document.readyState === 'complete') {{
                initZohoSDK();
            }} else {{
                window.addEventListener('load', initZohoSDK);
            }}
            
            // ================================================================
            // OAUTH POPUP COMMUNICATION
            // ================================================================
            
            window.addEventListener('message', function(event) {{
                try {{
                    var data = event.data;
                    if (data && data.type === 'oauth_success') {{
                        var orgId = data.org_id || currentOrgId;
                        if (orgId && orgId !== 'N/A') {{
                            window.location.href = '/dashboard?org_id=' + orgId;
                        }} else {{
                            window.location.reload();
                        }}
                    }}
                }} catch(e) {{ }}
            }});
            
            function checkLocalStorageForOAuth() {{
                try {{
                    var oauthData = localStorage.getItem('oauth_complete');
                    if (oauthData) {{
                        var data = JSON.parse(oauthData);
                        if (Date.now() - data.timestamp < 30000) {{
                            localStorage.removeItem('oauth_complete');
                            if (data.org_id) {{
                                window.location.href = '/dashboard?org_id=' + data.org_id;
                            }} else {{
                                window.location.reload();
                            }}
                        }} else {{
                            localStorage.removeItem('oauth_complete');
                        }}
                    }}
                }} catch(e) {{ }}
            }}
            
            checkLocalStorageForOAuth();
            setInterval(checkLocalStorageForOAuth, 2000);
            
            window.addEventListener('focus', function() {{
                setTimeout(checkLocalStorageForOAuth, 500);
                if (isZohoInitialized) {{
                    setTimeout(fetchZohoOrgId, 1000);
                }}
            }});
        }})();
    </script>
</body>
</html>
"""

# =============================================================================
# ZOHO CARD TEMPLATES (Connected / Not Connected)
# =============================================================================

ZOHO_LOGO_SVG = '''<svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg" class="logo-svg">
    <style>.st1{fill:#fff}</style>
    <circle cx="512" cy="512" r="512" style="fill:#2378c7"></circle>
    <g transform="scale(0.8) translate(128, 128)">
        <path class="st1" d="M810.3 452.6 829 431v147.8l-18.7 18.7V452.6zm-137.7-2.4h135.2l19-21.9-134.2.1m45.2 62.6c-9.3 0-16.4 3.2-21.7 9.6-5.3 6.4-7.9 15.2-7.9 26.6 0 11.2 2.7 19.9 8 26.2 5.3 6.3 12.4 9.5 21.6 9.5 9.2 0 16.3-3.2 21.5-9.5 5.3-6.4 7.9-15.1 7.9-26.2 0-11.4-2.7-20.2-7.9-26.6-5.2-6.4-12.3-9.6-21.5-9.6zm69.1-37.4v145.5H671.1V453.6h135.8zm-15.2 73.6c0-8-1.4-15.5-4.1-22.3-2.7-6.8-6.7-13-12.1-18.4-5.1-5.2-10.8-9.1-17.2-11.8-6.3-2.6-13.2-3.9-20.5-3.9-7.4 0-14.3 1.3-20.7 3.9-6.4 2.6-12.1 6.6-17.2 11.8-5.3 5.4-9.3 11.5-12 18.3-2.7 6.8-4 14.3-4 22.4 0 8 1.3 15.4 4 22.3s6.7 13.1 12 18.5c4.9 5.1 10.6 9 17 11.6 6.4 2.6 13.3 3.9 20.9 3.9 7.3 0 14.1-1.3 20.5-3.9 6.4-2.6 12.1-6.5 17.2-11.6 5.3-5.5 9.4-11.6 12.1-18.5 2.7-6.8 4.1-14.3 4.1-22.3z"></path>
        <path class="st1" d="m675.2 552-9 25.1L648 448.7l10.1-28.9m-133.4 45.3-.2-1.7L645 447l10.7-30.6-133.4 18.5-9.5 31.8 11.9-1.6zm138.6 115.6-131.7 18.5-17.9-126 13.4 6 .7-1.5-.5-2.1-14.1-6.4-.4-2.5 11.8-1.6.4 1.7 119.7-16.3 18.6 130.2zm-26.4-14.4c0-1-.1-2.1-.3-3.3l-13.1-89.3c-.6-4.1-2-7.2-4.3-9.3-1.8-1.6-4.1-2.5-6.7-2.5-.7 0-1.3.1-2 .2-3.5.5-6.1 2.1-7.7 4.7-1.2 1.9-1.8 4.2-1.8 6.9 0 1 .1 2.1.3 3.2l4.9 34.3-38.3 5.6-4.9-34.3c-.6-4-2-7.1-4.2-9.2-1.8-1.7-4.1-2.6-6.6-2.6-.6 0-1.2 0-1.8.1-3.6.5-6.4 2.1-8 4.7-1.2 1.9-1.8 4.2-1.8 6.9 0 1 .1 2.1.3 3.3L554 575c.6 4.1 2 7.2 4.4 9.2 1.8 1.6 4.1 2.4 6.8 2.4.7 0 1.5-.1 2.2-.2 3.3-.5 5.9-2.1 7.4-4.7 1.1-1.9 1.6-4.1 1.6-6.7 0-1-.1-2.1-.3-3.3l-5.4-35.3 38.3-5.6 5.4 35.3c.6 4.1 2 7.2 4.3 9.2 1.8 1.6 4.1 2.4 6.7 2.4.7 0 1.3-.1 2.1-.2 3.4-.5 6.1-2.1 7.7-4.7 1.2-1.6 1.7-3.9 1.7-6.5z"></path>
        <path class="st1" d="m353.6 543-6.2-47 47.2-111.9 11.7 39.4L357.6 534l-4 9zm101.9-65.8c-3.9-1.7-7.7-2.5-11.4-2.5-4.2 0-8.3 1.1-12.2 3.2-7.4 4.1-13.4 11.5-18 22.4-3 7.1-4.5 13.6-4.5 19.6 0 3 .4 5.9 1.1 8.6 2.3 8.1 7.5 13.8 15.9 17.4 3.9 1.6 7.6 2.5 11.3 2.5 4.2 0 8.2-1.1 12.2-3.2 7.4-4 13.3-11.3 17.8-22 3.1-7.3 4.6-14 4.6-20.1 0-2.9-.4-5.7-1.1-8.4-2.3-8.2-7.4-13.9-15.7-17.5zm62.2-39.6-120.1-55 11.8 39.8 117.8 53.2m-.1 3.6-53.3 121.1L355.6 547v-.1l53.3-121 118.2 53.3zm-31.9 30.6v-2.2c0-6.8-1.2-13.5-3.6-20-2.5-6.9-6.2-12.9-10.9-17.8-4.7-5-10.4-8.9-17.1-11.7-6.7-2.8-13.4-4.2-20.2-4.2h-.3c-6.9 0-13.7 1.6-20.4 4.6-7 3.1-13.1 7.3-18.3 12.8-5.2 5.5-9.4 12.1-12.7 19.8-3.2 7.6-5 15.2-5.3 22.8 0 .9-.1 1.7-.1 2.6 0 6.7 1.2 13.3 3.4 19.7 2.4 6.8 6 12.6 10.8 17.6 4.7 4.9 10.6 8.9 17.5 11.8 6.6 2.8 13.3 4.2 20.1 4.2h.2c6.8 0 13.6-1.5 20.3-4.4 7.1-3.2 13.2-7.5 18.5-13 5.2-5.5 9.5-12.1 12.7-19.7 3.3-7.8 5.1-15.4 5.4-22.9z"></path>
        <path class="st1" d="m349.5 573.2-19-124.8 8.1-42.3 18.8 126-7.9 41.1zm-2.6 5.2-130.7 20.5-21-128.4 132.2-20.2 19.5 128.1zm-30.1-14.1c0-.7-.1-1.4-.2-2.2-.3-1.8-1-3.4-2-4.6-1-1.2-2.4-2.2-4.2-2.8-1.8-.6-3.9-.9-6.4-.9-2.4 0-5.1.3-8.1.8l-34.9 6c.4-2.7 1.7-6.2 4.1-10.5 2.6-4.8 6.5-10.6 11.6-17.4 1.8-2.4 3.1-4.1 4-5.4.7-.8 1.6-2 2.8-3.6 8-10.5 12.9-19 14.8-25.7 1.1-3.8 1.7-7.6 2-11.5.1-1.1.1-2.1.1-3.1 0-2.8-.2-5.5-.7-8.2-.4-2.4-1-4.5-1.8-6.1-.8-1.6-1.8-2.9-3.1-3.6-1.4-.9-3.4-1.2-6-1.2-2.2 0-4.8.3-7.8.8l-40.4 6.9c-4.9.8-8.5 2.3-10.8 4.4-1.8 1.7-2.8 3.9-2.8 6.5 0 .7.1 1.4.2 2.1.6 3.4 2.4 5.9 5.2 7.2 1.7.8 3.8 1.1 6.2 1.1 1.6 0 3.4-.2 5.4-.5l33.8-5.7c.1.6.1 1.2.1 1.8 0 2.1-.4 4.2-1.1 6.2-1 2.8-3.5 6.8-7.5 11.9-1.1 1.4-2.9 3.5-5.2 6.5-9.1 11-15.6 20.4-19.6 28.3-2.8 5.4-4.7 10.7-5.8 15.9-.6 3-.9 6-.9 8.8 0 2 .2 4 .5 5.8.5 2.7 1.1 4.9 2 6.7.9 1.8 2 3.1 3.9 3.5 1.3.7 3.3 1 5.9 1 3.4 0 7.9-.5 13.7-1.5l36.6-6.3c6.5-1.1 11-2.7 13.6-4.8 2.2-1.9 3.3-4.3 3.2-7zM204.3 422.5l-6.7 33.3-2.3 11.3 132.1-20.2 8.7-45.5-131.8 21.1z"></path>
    </g>
</svg>'''

# Escape curly braces for use in formatted strings (e.g. ZOHO_CARD_CONNECTED)
# This changes {fill:#fff} to {{fill:#fff}} so .format() doesn't treat it as a key
ZOHO_LOGO_SVG_ESCAPED = ZOHO_LOGO_SVG.replace('{', '{{').replace('}', '}}')

SLACK_LOGO_SVG = '''<svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" class="logo-svg">
    <path d="M26.5002 14.9996C27.8808 14.9996 29 13.8804 29 12.4998C29 11.1192 27.8807 10 26.5001 10C25.1194 10 24 11.1193 24 12.5V14.9996H26.5002ZM19.5 14.9996C20.8807 14.9996 22 13.8803 22 12.4996V5.5C22 4.11929 20.8807 3 19.5 3C18.1193 3 17 4.11929 17 5.5V12.4996C17 13.8803 18.1193 14.9996 19.5 14.9996Z" fill="#2EB67D"></path>
    <path d="M5.49979 17.0004C4.11919 17.0004 3 18.1196 3 19.5002C3 20.8808 4.1193 22 5.49989 22C6.8806 22 8 20.8807 8 19.5V17.0004H5.49979ZM12.5 17.0004C11.1193 17.0004 10 18.1197 10 19.5004V26.5C10 27.8807 11.1193 29 12.5 29C13.8807 29 15 27.8807 15 26.5V19.5004C15 18.1197 13.8807 17.0004 12.5 17.0004Z" fill="#E01E5A"></path>
    <path d="M17.0004 26.5002C17.0004 27.8808 18.1196 29 19.5002 29C20.8808 29 22 27.8807 22 26.5001C22 25.1194 20.8807 24 19.5 24L17.0004 24L17.0004 26.5002ZM17.0004 19.5C17.0004 20.8807 18.1197 22 19.5004 22L26.5 22C27.8807 22 29 20.8807 29 19.5C29 18.1193 27.8807 17 26.5 17L19.5004 17C18.1197 17 17.0004 18.1193 17.0004 19.5Z" fill="#ECB22E"></path>
    <path d="M14.9996 5.49979C14.9996 4.11919 13.8804 3 12.4998 3C11.1192 3 10 4.1193 10 5.49989C10 6.88061 11.1193 8 12.5 8L14.9996 8L14.9996 5.49979ZM14.9996 12.5C14.9996 11.1193 13.8803 10 12.4996 10L5.5 10C4.11929 10 3 11.1193 3 12.5C3 13.8807 4.11929 15 5.5 15L12.4996 15C13.8803 15 14.9996 13.8807 14.9996 12.5Z" fill="#36C5F0"></path>
</svg>'''

# Zoho Card - Not Connected (Uses standard SVG, no formatting)
ZOHO_CARD_NOT_CONNECTED = '''
<div class="card">
    <div class="card-header">
        <div class="brand-section">
            <div class="logo-box">
                ''' + ZOHO_LOGO_SVG + '''
            </div>
            <div>
                <div class="brand-title">Zoho CRM</div>
                <div class="brand-subtitle">Decisions in CRM</div>
            </div>
        </div>
        <span class="status-badge">Not Connected</span>
    </div>
    <div class="card-body">
        <p class="description">Authenticate with your Zoho CRM account to view and manage decisions directly within your CRM records.</p>
        <button class="btn btn-primary" onclick="startZohoOAuth()">
            Connect Zoho CRM
        </button>
    </div>
</div>
'''

# Zoho Card - Connected (Uses ESCAPED SVG because this string is formatted)
ZOHO_CARD_CONNECTED = '''
<div class="card">
    <div class="card-header">
        <div class="brand-section">
            <div class="logo-box">
                ''' + ZOHO_LOGO_SVG_ESCAPED + '''
            </div>
            <div>
                <div class="brand-title">Zoho CRM</div>
                <div class="brand-subtitle">Decisions in CRM</div>
            </div>
        </div>
        <div class="badge-active">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            Active
        </div>
    </div>

    <div class="grid-container">
        <div class="grid-item">
            <span class="label">Organization ID</span>
            <span class="value">{org_id}</span>
        </div>
        <div class="grid-item">
            <span class="label">Data Center</span>
            <span class="value">{data_center}</span>
        </div>
    </div>

    <div class="card-footer">
        <div class="date-meta">Connected Since {connected_date}</div>
        <button class="btn-disconnect" onclick="if(confirm('Disconnect Zoho CRM?')) window.location.href='/zoho/disconnect?org_id={org_id}'">Disconnect</button>
    </div>
</div>
'''

# Slack Card - Locked (Zoho not connected)
SLACK_CARD_LOCKED = '''
<div class="card locked-card">
    <div class="card-header">
        <div class="brand-section">
            <div class="logo-box">
                ''' + SLACK_LOGO_SVG + '''
            </div>
            <div>
                <div class="brand-title">Slack</div>
                <div class="brand-subtitle">Decisions & Voting</div>
            </div>
        </div>
        <span class="status-badge">Locked</span>
    </div>
    <div class="card-body">
        <p class="description">Requires Zoho CRM connection first. Once connected, you can propose decisions and vote directly from Slack.</p>
        <button class="btn btn-disabled" disabled>
            Connect Slack
        </button>
    </div>
</div>
'''

# Slack Card - Not Connected (Zoho connected, Slack not)
SLACK_CARD_NOT_CONNECTED = '''
<div class="card">
    <div class="card-header">
        <div class="brand-section">
            <div class="logo-box">
                ''' + SLACK_LOGO_SVG + '''
            </div>
            <div>
                <div class="brand-title">Slack</div>
                <div class="brand-subtitle">Decisions & Voting</div>
            </div>
        </div>
        <span class="status-badge">Not Connected</span>
    </div>
    <div class="card-body">
        <p class="description">Connect Slack to propose decisions, cast votes, and collaborate with your team directly in your workspace.</p>
        <button onclick="startSlackOAuth('{org_id}')" class="btn btn-primary">
            Connect Slack
        </button>
    </div>
</div>
'''

# Slack Card - Connected (template with placeholders)
SLACK_CARD_CONNECTED = '''
<div class="card">
    <div class="card-header">
        <div class="brand-section">
            <div class="logo-box">
                ''' + SLACK_LOGO_SVG + '''
            </div>
            <div>
                <div class="brand-title">Slack</div>
                <div class="brand-subtitle">Decisions & Voting</div>
            </div>
        </div>
        <div class="badge-active">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            Active
        </div>
    </div>

    <div class="grid-container">
        <div class="grid-item">
            <span class="label">Workspace</span>
            <span class="value">{workspace_name}</span>
        </div>
        <div class="grid-item">
            <span class="label">Team ID</span>
            <span class="value">{team_id}</span>
        </div>
    </div>

    <div class="card-footer">
        <div class="date-meta">Connected Since {connected_date}</div>
        <button class="btn-disconnect" onclick="if(confirm('Disconnect Slack?')) window.location.href='/slack/disconnect?org_id={org_id}'">Disconnect</button>
    </div>
</div>
'''

# Alert HTML templates
ALERT_SETUP_HTML = '''
<div class="alert-setup">
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line>
    </svg>
    <span>Please connect Zoho CRM first to enable the data pipeline.</span>
</div>
'''

# Quick Commands Section (shown when both connected)
COMMANDS_SECTION_HTML = '''
<div class="commands-card">
    <div class="commands-title">Quick Commands</div>
    <div class="command-row">
        <div class="cmd-pill">/decision help</div>
        <div class="cmd-desc">to view all the commands</div>
    </div>
    <div class="command-row">
        <div class="cmd-pill">/decision propose "text"</div>
        <div class="cmd-desc">Create a new decision</div>
    </div>
    <div class="command-row">
        <div class="cmd-pill">/decision approve &lt;id&gt;</div>
        <div class="cmd-desc">Vote YES</div>
    </div>
    <div class="command-row">
        <div class="cmd-pill">/decision reject &lt;id&gt;</div>
        <div class="cmd-desc">Vote NO</div>
    </div>
</div>
'''


