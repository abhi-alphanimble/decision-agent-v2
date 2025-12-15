"""
HTML templates for Slack app pages.

These are served for OAuth success, privacy policy, and support pages.
"""

# ... (existing SUCCESS_PAGE_HTML, PRIVACY_PAGE_HTML, SUPPORT_PAGE_HTML, ERROR_PAGE_HTML)
# I'm adding new templates at the end of this file

# =============================================================================
# ZOHO OAUTH SUCCESS PAGE
# =============================================================================

ZOHO_SUCCESS_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zoho CRM Connected! - Decision Agent</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
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
        
        .success-icon {{
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 24px;
            animation: scaleIn 0.6s ease-out 0.2s backwards;
        }}
        
        @keyframes scaleIn {{
            from {{
                transform: scale(0);
            }}
            to {{
                transform: scale(1);
            }}
        }}
        
        .success-icon svg {{
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
        
        .info-box {{
            background: #f7fafc;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 24px;
            text-align: left;
        }}
        
        .info-item {{
            display: flex;
            align-items: flex-start;
            margin-bottom: 12px;
        }}
        
        .info-item:last-child {{
            margin-bottom: 0;
        }}
        
        .info-item-icon {{
            color: #38ef7d;
            font-size: 20px;
            margin-right: 12px;
            flex-shrink: 0;
        }}
        
        .info-item-text {{
            color: #2d3748;
            font-size: 14px;
            line-height: 1.5;
        }}
        
        .team-info {{
            background: #e6fffa;
            border-left: 4px solid #38ef7d;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 24px;
            text-align: left;
        }}
        
        .team-info-label {{
            color: #2c7a7b;
            font-size: 12px;
            text-transform: uppercase;
            font-weight: 600;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        
        .team-info-value {{
            color: #1a202c;
            font-size: 16px;
            font-weight: 600;
        }}
        
        .btn {{
            display: inline-block;
            padding: 14px 32px;
            font-size: 16px;
            font-weight: 600;
            text-decoration: none;
            border-radius: 8px;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
            box-shadow: 0 4px 12px rgba(56, 239, 125, 0.3);
        }}
        
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(56, 239, 125, 0.4);
        }}
        
        .footer {{
            margin-top: 32px;
            padding-top: 24px;
            border-top: 1px solid #e2e8f0;
            color: #718096;
            font-size: 14px;
        }}
        
        .footer a {{
            color: #11998e;
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
        <div class="success-icon">
            <svg viewBox="0 0 24 24">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
        </div>
        
        <h1>✅ Zoho CRM Connected!</h1>
        
        <p class="subtitle">
            Your team's Zoho CRM account has been successfully connected to Decision Agent.
        </p>
        
        <div class="team-info">
            <div class="team-info-label">Connected Team</div>
            <div class="team-info-value">{team_name}</div>
        </div>
        
        <div class="info-box">
            <div class="info-item">
                <span class="info-item-icon">🔄</span>
                <div class="info-item-text">
                    <strong>Automatic Sync:</strong> All decisions will now sync to your Zoho CRM automatically
                </div>
            </div>
            <div class="info-item">
                <span class="info-item-icon">🔐</span>
                <div class="info-item-text">
                    <strong>Secure Storage:</strong> Your credentials are encrypted and stored securely
                </div>
            </div>
            <div class="info-item">
                <span class="info-item-icon">👥</span>
                <div class="info-item-text">
                    <strong>Team-Wide:</strong> All team members' decisions will sync to the same Zoho account
                </div>
            </div>
        </div>
        
        <p style="color: #4a5568; font-size: 14px; margin-bottom: 24px;">
            You can now close this window and return to Slack.
        </p>
        
        <a href="slack://open" class="btn btn-primary">Return to Slack</a>
        
        <div class="footer">
            Need help? <a href="/support">Contact Support</a>
        </div>
    </div>
</body>
</html>
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
# ZOHO DASHBOARD PAGE
# =============================================================================

ZOHO_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Integrations Dashboard - Decision Agent</title>
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
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">📊</div>
        <h1>Integrations Dashboard</h1>
        <p class="team-name">Team: {team_name}</p>
    </div>
    
    <div class="container">
        {alert_html}
        
        <!-- Slack Integration Card -->
        <div class="card">
            <div class="card-header">
                <div class="card-title">
                    <span class="card-icon">💬</span>
                    <span class="card-title-text">Slack</span>
                </div>
                <span class="status-badge status-connected">Connected</span>
            </div>
            <div class="card-body">
                <p>Your Slack workspace is connected to Decision Agent.</p>
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
            </div>
        </div>
        
        <!-- Zoho CRM Integration Card -->
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
    </div>
    
    <div class="footer">
        Need help? <a href="/support">Contact Support</a> | 
        <a href="/privacy">Privacy Policy</a>
    </div>
</body>
</html>
"""
