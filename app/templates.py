"""
HTML templates for Slack app pages.

These are served for OAuth success, privacy policy, and support pages.
"""

SUCCESS_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Installation Successful - Decision Agent</title>
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
            padding: 48px;
            max-width: 500px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        
        .emoji {{
            font-size: 64px;
            margin-bottom: 24px;
        }}
        
        h1 {{
            color: #1a1a2e;
            font-size: 28px;
            margin-bottom: 16px;
        }}
        
        .team-name {{
            color: #667eea;
            font-weight: 600;
        }}
        
        p {{
            color: #666;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 24px;
        }}
        
        .commands {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: left;
            margin-bottom: 24px;
        }}
        
        .commands h3 {{
            color: #333;
            font-size: 14px;
            margin-bottom: 12px;
        }}
        
        .command {{
            font-family: 'Monaco', 'Menlo', monospace;
            background: #e9ecef;
            padding: 8px 12px;
            border-radius: 4px;
            font-size: 13px;
            margin-bottom: 8px;
            color: #495057;
        }}
        
        .command:last-child {{
            margin-bottom: 0;
        }}
        
        .btn {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            padding: 14px 32px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        }}
        
        .footer {{
            margin-top: 24px;
            font-size: 12px;
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">🎉</div>
        <h1>Installation Successful!</h1>
        <p>
            Decision Agent has been installed to 
            <span class="team-name">{team_name}</span>
        </p>
        
        <div class="commands">
            <h3>Get Started with These Commands:</h3>
            <div class="command">/decision help</div>
            <div class="command">/decision propose "Your proposal"</div>
            <div class="command">/decision list</div>
        </div>
        
        <a href="slack://app?team={team_id}" class="btn">Open in Slack</a>
        
        <p class="footer">
            Need help? Contact us at support@decisionagent.ai
        </p>
    </div>
</body>
</html>
"""


PRIVACY_POLICY_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy - Decision Agent | DeciAgent</title>
    <meta name="description" content="Privacy Policy for Decision Agent (DeciAgent) - Learn how we collect, use, and protect your data when using our Slack decision-making application.">
    <style>
        :root {
            --bg-body: #f1f5f9;
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --border: #e2e8f0;
            --radius: 12px;
            --success: #10b981;
            --success-bg: #dcfce7;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.6;
            padding: 40px 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .back-button {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-muted);
            text-decoration: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
            margin-bottom: 24px;
        }
        
        .back-button:hover {
            background: #f8fafc;
            color: var(--primary);
            border-color: var(--primary);
        }
        
        .back-button svg {
            width: 16px;
            height: 16px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 32px;
        }
        
        .header-icon {
            width: 48px;
            height: 48px;
            margin: 0 auto 16px;
            display: block;
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
            color: var(--text-main);
        }
        
        .header p {
            color: var(--text-muted);
            font-size: 15px;
            font-weight: 500;
        }
        
        .card {
            background: var(--bg-card);
            border-radius: var(--radius);
            padding: 24px;
            margin-bottom: 16px;
            border: 1px solid var(--border);
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        
        h2 {
            color: var(--text-main);
            margin-bottom: 12px;
            font-size: 16px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        h2 .icon {
            font-size: 16px;
        }
        
        h3 {
            color: var(--text-main);
            font-size: 14px;
            font-weight: 600;
            margin: 16px 0 8px;
        }
        
        p {
            color: var(--text-muted);
            font-size: 14px;
            line-height: 1.7;
            margin-bottom: 12px;
        }
        
        ul {
            padding-left: 20px;
            margin-bottom: 12px;
        }
        
        li {
            margin-bottom: 8px;
            color: var(--text-muted);
            font-size: 14px;
            line-height: 1.6;
        }
        
        li strong {
            color: var(--text-main);
            font-weight: 600;
        }
        
        .highlight-box {
            background: #eff6ff;
            border: 1px solid #dbeafe;
            border-radius: 8px;
            padding: 16px;
            margin: 12px 0;
        }
        
        .highlight-box p {
            margin: 0;
            color: #1e40af;
            font-weight: 500;
        }
        
        .third-party-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            margin-top: 12px;
        }
        
        .third-party-item {
            background: #f8fafc;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            border: 1px solid var(--border);
        }
        
        .third-party-item strong {
            display: block;
            color: var(--text-main);
            margin-bottom: 4px;
            font-size: 14px;
        }
        
        .third-party-item span {
            color: var(--text-muted);
            font-size: 12px;
        }
        
        .contact-section {
            text-align: center;
            padding: 32px;
            background: var(--bg-card);
            border-radius: var(--radius);
            border: 1px solid var(--border);
            margin-top: 24px;
        }
        
        .contact-section h2 {
            justify-content: center;
            margin-bottom: 8px;
        }
        
        .contact-email {
            display: inline-block;
            color: var(--primary);
            font-weight: 600;
            font-size: 16px;
            text-decoration: none;
            padding: 10px 20px;
            background: #eff6ff;
            border: 1px solid #dbeafe;
            border-radius: 8px;
            margin-top: 12px;
            transition: all 0.2s;
        }
        
        .contact-email:hover {
            background: #dbeafe;
        }
        
        .footer {
            max-width: 800px;
            margin: 32px auto 0;
            text-align: center;
            color: var(--text-muted);
            font-size: 13px;
            padding-top: 24px;
            border-top: 1px solid var(--border);
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 24px;
            margin-top: 12px;
        }
        
        .footer-links a {
            color: var(--primary);
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
        }
        
        .footer-links a:hover {
            text-decoration: underline;
        }
        
        a {
            color: var(--primary);
        }
        
        @media (max-width: 640px) {
            .container {
                padding: 0;
            }
            
            body {
                padding: 24px 16px;
            }
            
            .card {
                padding: 20px;
            }
            
            .third-party-grid {
                grid-template-columns: 1fr 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/dashboard" class="back-button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Back to Dashboard
        </a>
        
        <div class="header">
            <svg class="header-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="5" y="11" width="14" height="10" rx="2" stroke="#2563eb" stroke-width="2"/>
                <path d="M7 11V7C7 4.23858 9.23858 2 12 2C14.7614 2 17 4.23858 17 7V11" stroke="#2563eb" stroke-width="2" stroke-linecap="round"/>
                <circle cx="12" cy="16" r="1.5" fill="#2563eb"/>
            </svg>
            <h1>Privacy Policy</h1>
            <p>Decision Agent (DeciAgent) for Slack & Zoho CRM</p>
        </div>
        
        <div class="card">
            <h2><span class="icon">📋</span> Introduction</h2>
            <p>
                Decision Agent, also known as DeciAgent ("we", "our", "us", or "the app"), is developed and operated by 
                <strong>Alphanimble Private Limited</strong>. We provide a Slack application that helps teams make group 
                decisions through a collaborative voting system, with optional integration to Zoho CRM for decision tracking.
            </p>
            <p>
                This Privacy Policy explains what information we collect, how we use it, how we protect it, 
                and your rights regarding your personal data. By using Decision Agent, you agree to the collection 
                and use of information in accordance with this policy.
            </p>
        </div>
        
        <div class="card">
            <h2><span class="icon">📊</span> Information We Collect</h2>
            <p>When you install and use Decision Agent, we collect and store the following types of information:</p>
            
            <h3>Slack Workspace Data</h3>
            <ul>
                <li><strong>Workspace Information:</strong> Team ID, team name, and enterprise ID (if applicable)</li>
                <li><strong>Bot Tokens:</strong> OAuth access tokens for API communication (encrypted at rest)</li>
                <li><strong>User Information:</strong> Slack user IDs and display names of users who interact with decisions</li>
                <li><strong>Channel Information:</strong> Channel IDs where decisions are created</li>
            </ul>
            
            <h3>Decision & Voting Data</h3>
            <ul>
                <li><strong>Proposals:</strong> Decision text, descriptions, and metadata submitted by users</li>
                <li><strong>Votes:</strong> Approval/rejection votes including voter identity and timestamp</li>
                <li><strong>Outcomes:</strong> Final decision status and resolution timestamps</li>
            </ul>
            
            <h3>Configuration Data</h3>
            <ul>
                <li><strong>Channel Settings:</strong> Approval thresholds, voting percentages, and custom configurations</li>
                <li><strong>Integration Settings:</strong> Zoho CRM connection status and organization IDs</li>
            </ul>
            
            <h3>Zoho CRM Data (If Connected)</h3>
            <ul>
                <li><strong>Organization Information:</strong> Zoho organization ID and data center location</li>
                <li><strong>OAuth Tokens:</strong> Access and refresh tokens for API communication (encrypted at rest)</li>
            </ul>
        </div>
        
        <div class="card">
            <h2><span class="icon">⚙️</span> How We Use Your Information</h2>
            <p>We use the collected information exclusively to provide and improve our services:</p>
            <ul>
                <li><strong>Core Functionality:</strong> Enable decision creation, voting, and outcome tracking within Slack</li>
                <li><strong>Notifications:</strong> Send decision updates and outcome notifications to relevant channels</li>
                <li><strong>AI Features:</strong> Provide AI-powered decision summaries and suggestions (optional feature)</li>
                <li><strong>Zoho Sync:</strong> Synchronize decisions to your Zoho CRM for record-keeping (if enabled)</li>
                <li><strong>Analytics:</strong> Generate usage statistics and dashboards for your organization</li>
                <li><strong>Service Improvement:</strong> Analyze aggregated, anonymized usage patterns to improve our app</li>
            </ul>
            
            <div class="highlight-box">
                <p>🔒 <strong>We do NOT:</strong> Sell your data, use it for advertising, or share it with third parties for marketing purposes.</p>
            </div>
        </div>
        
        <div class="card">
            <h2><span class="icon">🔗</span> Third-Party Services</h2>
            <p>Decision Agent integrates with and may share data with the following third-party services as part of its functionality:</p>
            
            <div class="third-party-grid">
                <div class="third-party-item">
                    <strong>Slack</strong>
                    <span>Messaging platform</span>
                </div>
                <div class="third-party-item">
                    <strong>Zoho CRM</strong>
                    <span>Decision sync (optional)</span>
                </div>
                <div class="third-party-item">
                    <strong>OpenAI / Google AI</strong>
                    <span>AI features</span>
                </div>
                <div class="third-party-item">
                    <strong>Zoho Catalyst</strong>
                    <span>Cloud hosting</span>
                </div>
            </div>
            
            <p style="margin-top: 16px;">
                Each third-party service has its own privacy policy. We recommend reviewing:
                <a href="https://slack.com/privacy-policy" target="_blank">Slack Privacy Policy</a>,
                <a href="https://www.zoho.com/privacy.html" target="_blank">Zoho Privacy Policy</a>,
                <a href="https://openai.com/privacy" target="_blank">OpenAI Privacy Policy</a>.
            </p>
        </div>
        
        <div class="card">
            <h2><span class="icon">🛡️</span> Data Storage & Security</h2>
            <p>We take the security of your data seriously and implement multiple layers of protection:</p>
            <ul>
                <li><strong>Encryption at Rest:</strong> All OAuth tokens and sensitive credentials are encrypted using Fernet/AES-256 encryption</li>
                <li><strong>Encryption in Transit:</strong> All data transmitted uses TLS 1.2+ encryption</li>
                <li><strong>Access Controls:</strong> Strict access controls limit who can access production systems</li>
                <li><strong>Secure Infrastructure:</strong> Hosted on enterprise-grade cloud infrastructure (Zoho Catalyst)</li>
                <li><strong>Regular Audits:</strong> We regularly review and update our security practices</li>
            </ul>
        </div>
        
        <div class="card">
            <h2><span class="icon">🤝</span> Data Sharing</h2>
            <p>We do not sell, rent, or trade your personal data. We may share data only in these circumstances:</p>
            <ul>
                <li><strong>With Your Consent:</strong> When you explicitly enable integrations (e.g., Zoho CRM sync)</li>
                <li><strong>Service Providers:</strong> With trusted vendors who help operate our service, bound by confidentiality agreements</li>
                <li><strong>Legal Requirements:</strong> If required by law, court order, or government request</li>
                <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets (with prior notice)</li>
            </ul>
        </div>
        
        <div class="card">
            <h2><span class="icon">⏰</span> Data Retention</h2>
            <p>We retain your data according to the following policies:</p>
            <ul>
                <li><strong>Active Installations:</strong> Data is retained as long as the app is installed</li>
                <li><strong>After Uninstallation:</strong> OAuth tokens are immediately deleted; decision data is retained for 30 days</li>
                <li><strong>Audit Logs:</strong> System logs are retained for 90 days</li>
                <li><strong>Backup Data:</strong> Backups are retained for 30 days and then automatically purged</li>
            </ul>
            <p>You may request immediate deletion of all your data at any time by contacting us.</p>
        </div>
        
        <div class="card">
            <h2><span class="icon">✅</span> Your Rights</h2>
            <p>Depending on your location, you may have the following rights regarding your personal data:</p>
            <ul>
                <li><strong>Right to Access:</strong> Request a copy of the data we hold about your organization</li>
                <li><strong>Right to Rectification:</strong> Request correction of inaccurate or incomplete data</li>
                <li><strong>Right to Erasure:</strong> Request deletion of your data ("right to be forgotten")</li>
                <li><strong>Right to Portability:</strong> Request your data in a machine-readable format</li>
                <li><strong>Right to Object:</strong> Object to certain processing activities</li>
                <li><strong>Right to Withdraw Consent:</strong> Withdraw consent at any time by uninstalling the app</li>
            </ul>
            <p>To exercise any of these rights, please contact us at the email address below.</p>
        </div>
        
        <div class="card">
            <h2><span class="icon">👶</span> Children's Privacy</h2>
            <p>
                Decision Agent is designed for business use and is not intended for children under 16 years of age. 
                We do not knowingly collect personal information from children. If you believe we have inadvertently 
                collected data from a child, please contact us immediately.
            </p>
        </div>
        
        <div class="card">
            <h2><span class="icon">🌍</span> International Data Transfers</h2>
            <p>
                Your data may be transferred to and processed in countries other than your own. Our servers are 
                located in the United States and other regions. We ensure appropriate safeguards are in place for 
                international transfers, including Standard Contractual Clauses where required by GDPR.
            </p>
        </div>
        
        <div class="card">
            <h2><span class="icon">🍪</span> Cookies & Tracking</h2>
            <p>
                Our web dashboard uses essential cookies for session management and authentication. We do not use 
                advertising or tracking cookies. The cookies we use are:
            </p>
            <ul>
                <li><strong>Session Cookies:</strong> Maintain your authenticated session while using the dashboard</li>
                <li><strong>Security Cookies:</strong> Help protect against CSRF and other security threats</li>
            </ul>
        </div>
        
        <div class="card">
            <h2><span class="icon">📝</span> Changes to This Policy</h2>
            <p>We may update this Privacy Policy from time to time. When we make significant changes, we will:</p>
            <ul>
                <li>Update the "Last Updated" date at the bottom of this page</li>
                <li>Notify workspace admins via Slack or email for material changes</li>
                <li>Post a notice on our dashboard for 30 days</li>
            </ul>
            <p>Continued use of the app after changes constitutes acceptance of the updated policy.</p>
        </div>
        
        <div class="contact-section">
            <h2><span class="icon">📧</span> Contact Us</h2>
            <p>
                If you have questions about this Privacy Policy, want to exercise your data rights, 
                or have any privacy concerns, please contact us:
            </p>
            <a href="mailto:info@alphanimble.com" class="contact-email">info@alphanimble.com</a>
            <p style="margin-top: 16px;">
                <strong>Alphanimble Private Limited</strong><br>
                Data Protection Inquiries
            </p>
        </div>
        
        <div class="footer">
            <p>Last updated: January 2026</p>
            <div class="footer-links">
                <a href="/terms">Terms of Service</a>
                <a href="/support">Support</a>
                <a href="/dashboard">Dashboard</a>
            </div>
        </div>
    </div>
    
    <script>
        // Dynamically set the back button URL with orgId if available
        (function() {
            var orgId = "{org_id}";
            
            if (!orgId || orgId === "") {
                var urlParams = new URLSearchParams(window.location.search);
                orgId = urlParams.get('orgId') || urlParams.get('org_id') || '';
            }
            
            var backButton = document.querySelector('.back-button');
            if (backButton && orgId && orgId !== "") {
                backButton.href = '/dashboard?orgId=' + encodeURIComponent(orgId);
            }
            
            var footerLinks = document.querySelectorAll('.footer-links a');
            footerLinks.forEach(function(link) {
                if (orgId && orgId !== "") {
                    var href = link.getAttribute('href');
                    if (href && !href.includes('orgId')) {
                        link.href = href + (href.includes('?') ? '&' : '?') + 'orgId=' + encodeURIComponent(orgId);
                    }
                }
            });
        })();
    </script>
</body>
</html>
"""


SUPPORT_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Support - Decision Agent</title>
    <style>
        :root {
            --bg-body: #f1f5f9;
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --border: #e2e8f0;
            --radius: 12px;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.5;
            padding: 24px 20px;
        }
        
        .container {
            background: var(--bg-card);
            border-radius: var(--radius);
            padding: 32px;
            max-width: 800px;
            margin: 0 auto;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            border: 1px solid var(--border);
        }
        
        .back-button {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-muted);
            text-decoration: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
            margin-bottom: 24px;
        }
        
        .back-button:hover {
            background: #f8fafc;
            color: var(--primary);
            border-color: var(--primary);
        }
        
        .back-button svg {
            width: 16px;
            height: 16px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 32px;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border);
        }
        
        .support-icon {
            width: 48px;
            height: 48px;
            margin: 0 auto 16px;
            display: block;
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
            color: var(--text-main);
        }
        
        .header p {
            color: var(--text-muted);
            font-size: 14px;
            font-weight: 500;
        }
        
        .section {
            margin-bottom: 32px;
        }
        
        h2 {
            color: var(--text-main);
            margin-bottom: 16px;
            font-size: 18px;
            font-weight: 700;
        }
        
        h3 {
            color: var(--primary);
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 16px;
            font-weight: 600;
        }
        
        p {
            color: var(--text-muted);
            margin-bottom: 12px;
            font-size: 14px;
            line-height: 1.6;
        }
        
        .command-list {
            background: #f8fafc;
            border-radius: 8px;
            padding: 16px;
            margin: 16px 0;
            border: 1px solid var(--border);
        }
        
        .cmd {
            font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
            background: #ffffff;
            padding: 10px 14px;
            border-radius: 6px;
            margin-bottom: 10px;
            display: flex;
            align-items: flex-start;
            gap: 12px;
            border: 1px solid var(--border);
        }
        
        .cmd:last-child {
            margin-bottom: 0;
        }
        
        .cmd code {
            font-weight: 600;
            color: var(--primary);
            min-width: 220px;
            font-size: 13px;
        }
        
        .cmd span {
            color: var(--text-muted);
            font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
            font-size: 13px;
        }
        
        .contact-section {
            text-align: center;
            padding: 32px 24px;
            background: #f8fafc;
            border-radius: 8px;
            margin-top: 32px;
            border: 1px solid var(--border);
        }
        
        .contact-section svg {
            width: 56px;
            height: 56px;
            margin: 0 auto 16px;
            display: block;
        }
        
        .contact-section h2 {
            margin-bottom: 8px;
        }
        
        .email-link {
            color: var(--primary);
            text-decoration: none;
            font-weight: 600;
            font-size: 16px;
        }
        
        .email-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/dashboard" class="back-button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Back to Dashboard
        </a>
        
        <div class="header">
            <svg class="support-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <g>
                    <path fill="#2563eb" d="M12 2C6.486 2 2 6.486 2 12v4.143C2 17.167 2.897 18 4 18h1a1 1 0 0 0 1-1v-5.143a1 1 0 0 0-1-1h-.908C4.648 6.987 7.978 4 12 4s7.352 2.987 7.908 6.857H19a1 1 0 0 0-1 1V18c0 1.103-.897 2-2 2h-2v-1h-4v3h6c2.206 0 4-1.794 4-4 1.103 0 2-.833 2-1.857V12c0-5.514-4.486-10-10-10z"></path>
                </g>
            </svg>
            <h1>Support</h1>
            <p>Decision Agent for Slack</p>
        </div>
        
        <div class="section">
            <h2>Available Commands</h2>
            <p>Here are all the commands you can use with Decision Agent:</p>
            
            <div class="command-list">
                <div class="cmd">
                    <code>/decision help</code>
                    <span>Show all available commands</span>
                </div>
                <div class="cmd">
                    <code>/decision propose "text"</code>
                    <span>Create a new proposal for voting</span>
                </div>
                <div class="cmd">
                    <code>/decision approve &lt;id&gt;</code>
                    <span>Vote to approve a decision</span>
                </div>
                <div class="cmd">
                    <code>/decision reject &lt;id&gt;</code>
                    <span>Vote to reject a decision</span>
                </div>
                <div class="cmd">
                    <code>/decision list [status]</code>
                    <span>List decisions (all, pending, approved, rejected)</span>
                </div>
                <div class="cmd">
                    <code>/decision show &lt;id&gt;</code>
                    <span>Show details of a specific decision</span>
                </div>
                <div class="cmd">
                    <code>/decision add "text"</code>
                    <span>Add a pre-approved decision</span>
                </div>
                <div class="cmd">
                    <code>/decision config</code>
                    <span>View/change channel settings</span>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Common Questions</h2>
            
            <h3>How does voting work?</h3>
            <p>
                When someone creates a proposal, it requires a certain percentage of channel members 
                to approve it (default is 60%). Once enough approvals are received, the decision is 
                marked as approved. If too many rejections are received, it's rejected.
            </p>
            
            <h3>Can I change my vote?</h3>
            <p>
                No, votes are final. This ensures the integrity of the decision-making process.
            </p>
            
            <h3>What happens if no one votes?</h3>
            <p>
                Decisions remain open until someone votes. They will stay in pending status 
                until they reach the approval threshold or are manually closed.
            </p>
            
            <h3>How do I change the approval percentage?</h3>
            <p>
                Use <code style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; color: var(--primary); font-size: 13px;">/decision config percentage 70</code> to set the required approval 
                percentage to 70% for the current channel.
            </p>
        </div>
        
        <div class="contact-section">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <g>
                    <path fill="#2563eb" d="M12 2C6.486 2 2 6.486 2 12v4.143C2 17.167 2.897 18 4 18h1a1 1 0 0 0 1-1v-5.143a1 1 0 0 0-1-1h-.908C4.648 6.987 7.978 4 12 4s7.352 2.987 7.908 6.857H19a1 1 0 0 0-1 1V18c0 1.103-.897 2-2 2h-2v-1h-4v3h6c2.206 0 4-1.794 4-4 1.103 0 2-.833 2-1.857V12c0-5.514-4.486-10-10-10z"></path>
                </g>
            </svg>
            <h2>Need More Help?</h2>
            <p>Contact our support team:</p>
            <a href="mailto:info@alphanimble.com" class="email-link">info@alphanimble.com</a>
        </div>
    </div>
    
    <script>
        // Dynamically set the back button URL with orgId if available
        (function() {
            // Get orgId from template (injected by backend) or URL params
            var orgId = "{org_id}";
            
            // If not in template, try to get from current URL params
            if (!orgId || orgId === "") {
                var urlParams = new URLSearchParams(window.location.search);
                orgId = urlParams.get('orgId') || urlParams.get('org_id') || '';
            }
            
            // Update the back button href
            var backButton = document.querySelector('.back-button');
            if (backButton && orgId && orgId !== "") {
                backButton.href = '/dashboard?orgId=' + encodeURIComponent(orgId);
            }
        })();
    </script>
</body>
</html>
"""



TERMS_OF_SERVICE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terms of Service - Decision Agent | DeciAgent</title>
    <meta name="description" content="Terms of Service for Decision Agent (DeciAgent) - Read our terms and conditions for using our Slack decision-making application.">
    <style>
        :root {
            --bg-body: #f1f5f9;
            --bg-card: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --border: #e2e8f0;
            --radius: 12px;
            --warning: #f59e0b;
            --warning-bg: #fef3c7;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.6;
            padding: 40px 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        
        .back-button {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 8px 16px;
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text-muted);
            text-decoration: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
            margin-bottom: 24px;
        }
        
        .back-button:hover {
            background: #f8fafc;
            color: var(--primary);
            border-color: var(--primary);
        }
        
        .back-button svg {
            width: 16px;
            height: 16px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 32px;
        }
        
        .header-icon {
            width: 48px;
            height: 48px;
            margin: 0 auto 16px;
            display: block;
        }
        
        .header h1 {
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 8px;
            color: var(--text-main);
        }
        
        .header p {
            color: var(--text-muted);
            font-size: 15px;
            font-weight: 500;
        }
        
        .card {
            background: var(--bg-card);
            border-radius: var(--radius);
            padding: 24px;
            margin-bottom: 16px;
            border: 1px solid var(--border);
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        
        h2 {
            color: var(--text-main);
            margin-bottom: 12px;
            font-size: 16px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        h2 .icon {
            font-size: 16px;
        }
        
        p {
            color: var(--text-muted);
            font-size: 14px;
            line-height: 1.7;
            margin-bottom: 12px;
        }
        
        ul {
            padding-left: 20px;
            margin-bottom: 12px;
        }
        
        li {
            margin-bottom: 8px;
            color: var(--text-muted);
            font-size: 14px;
            line-height: 1.6;
        }
        
        li strong {
            color: var(--text-main);
            font-weight: 600;
        }
        
        .highlight-box {
            background: #eff6ff;
            border: 1px solid #dbeafe;
            border-radius: 8px;
            padding: 16px;
            margin: 12px 0;
        }
        
        .highlight-box p {
            margin: 0;
            color: #1e40af;
            font-weight: 500;
        }
        
        .warning-box {
            background: var(--warning-bg);
            border: 1px solid #fcd34d;
            border-radius: 8px;
            padding: 16px;
            margin: 12px 0;
        }
        
        .warning-box p {
            margin: 0;
            color: #92400e;
            font-weight: 500;
        }
        
        .ai-limits-table {
            width: 100%;
            margin: 12px 0;
            border-collapse: collapse;
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .ai-limits-table th,
        .ai-limits-table td {
            padding: 12px 16px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        
        .ai-limits-table th {
            background: #f8fafc;
            color: var(--text-main);
            font-weight: 600;
            font-size: 13px;
        }
        
        .ai-limits-table td {
            color: var(--text-muted);
            font-size: 14px;
        }
        
        .ai-limits-table tr:last-child td {
            border-bottom: none;
        }
        
        .contact-section {
            text-align: center;
            padding: 32px;
            background: var(--bg-card);
            border-radius: var(--radius);
            border: 1px solid var(--border);
            margin-top: 24px;
        }
        
        .contact-section h2 {
            justify-content: center;
            margin-bottom: 8px;
        }
        
        .contact-email {
            display: inline-block;
            color: var(--primary);
            font-weight: 600;
            font-size: 16px;
            text-decoration: none;
            padding: 10px 20px;
            background: #eff6ff;
            border: 1px solid #dbeafe;
            border-radius: 8px;
            margin-top: 12px;
            transition: all 0.2s;
        }
        
        .contact-email:hover {
            background: #dbeafe;
        }
        
        .footer {
            max-width: 800px;
            margin: 32px auto 0;
            text-align: center;
            color: var(--text-muted);
            font-size: 13px;
            padding-top: 24px;
            border-top: 1px solid var(--border);
        }
        
        .footer-links {
            display: flex;
            justify-content: center;
            gap: 24px;
            margin-top: 12px;
        }
        
        .footer-links a {
            color: var(--primary);
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
        }
        
        .footer-links a:hover {
            text-decoration: underline;
        }
        
        a {
            color: var(--primary);
        }
        
        @media (max-width: 640px) {
            .container {
                padding: 0;
            }
            
            body {
                padding: 24px 16px;
            }
            
            .card {
                padding: 20px;
            }
            
            .ai-limits-table {
                font-size: 12px;
            }
            
            .ai-limits-table th,
            .ai-limits-table td {
                padding: 8px 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="/dashboard" class="back-button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
            </svg>
            Back to Dashboard
        </a>
        
        <div class="header">
            <svg class="header-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M14 2V8H20" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M16 13H8" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M16 17H8" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10 9H9H8" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <h1>Terms of Service</h1>
            <p>Decision Agent (DeciAgent) for Slack & Zoho CRM</p>
        </div>
        
        <div class="card">
            <h2><span class="icon">📋</span> Acceptance of Terms</h2>
            <p>
                By installing, accessing, or using Decision Agent (also known as "DeciAgent", "the app", "the service", "we", "us", or "our"), 
                you agree to be bound by these Terms of Service ("Terms"). If you are accepting these Terms on behalf of a company or 
                other legal entity, you represent that you have the authority to bind such entity to these Terms.
            </p>
            <div class="highlight-box">
                <p><strong>Important:</strong> If you do not agree to these Terms, do not install or use Decision Agent.</p>
            </div>
            <p>
                Decision Agent is developed and operated by <strong>Alphanimble Private Limited</strong>. These Terms constitute a 
                legally binding agreement between you and Alphanimble Private Limited.
            </p>
        </div>
        
        <div class="card">
            <h2><span class="icon">🎯</span> Description of Service</h2>
            <p>Decision Agent is a collaborative decision-making application that provides:</p>
            <ul>
                <li><strong>Decision Tracking:</strong> Create, track, and manage group decisions within Slack channels</li>
                <li><strong>Voting System:</strong> Enable team members to approve or reject proposals with configurable thresholds</li>
                <li><strong>AI Features:</strong> Optional AI-powered decision summaries and suggestions (subject to usage limits)</li>
                <li><strong>Zoho CRM Integration:</strong> Optionally sync decisions to Zoho CRM for record-keeping and analytics</li>
                <li><strong>Dashboard:</strong> Web-based dashboard for viewing decision history and managing integrations</li>
            </ul>
        </div>
        
        <div class="card">
            <h2><span class="icon">🔐</span> Account & Access Requirements</h2>
            <p>To use Decision Agent, you must:</p>
            <ul>
                <li><strong>Slack Account:</strong> Have an active Slack workspace with appropriate permissions to install apps</li>
                <li><strong>Authorization:</strong> Authorize the app to access your Slack workspace during installation</li>
                <li><strong>Channel Access:</strong> Add the Decision Agent bot to channels where you want to use it</li>
                <li><strong>Zoho CRM (Optional):</strong> Have a valid Zoho CRM account if you wish to enable CRM integration</li>
            </ul>
            <p>
                You are responsible for maintaining the security of your Slack workspace and promptly notifying us 
                of any unauthorized access or security breaches.
            </p>
        </div>
        
        <div class="card">
            <h2><span class="icon">✅</span> Acceptable Use</h2>
            <p>You agree to use Decision Agent only for lawful purposes and in accordance with these Terms. You agree NOT to:</p>
            <ul>
                <li><strong>Abuse the Service:</strong> Send spam, make excessive API calls, or attempt to disrupt the service</li>
                <li><strong>Circumvent Limits:</strong> Attempt to bypass AI command limits or other usage restrictions</li>
                <li><strong>Reverse Engineer:</strong> Decompile, disassemble, or reverse engineer any part of the service</li>
                <li><strong>Unauthorized Access:</strong> Attempt to access other users' data or admin functions without authorization</li>
                <li><strong>Harmful Content:</strong> Use the service to create or distribute harmful, offensive, or illegal content</li>
                <li><strong>Misrepresent:</strong> Impersonate others or misrepresent your affiliation with any person or entity</li>
            </ul>
        </div>
        
        <div class="card">
            <h2><span class="icon">🤖</span> AI Features & Usage Limits</h2>
            <p>
                Decision Agent includes optional AI-powered features that are subject to usage limits. These limits exist to 
                ensure fair usage and service availability for all users.
            </p>
            
            <table class="ai-limits-table">
                <thead>
                    <tr>
                        <th>Feature</th>
                        <th>Monthly Limit</th>
                        <th>Reset Date</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>AI Summaries (/decision summarize)</td>
                        <td>100 commands per organization</td>
                        <td>1st of each month</td>
                    </tr>
                    <tr>
                        <td>AI Suggestions (/decision suggest)</td>
                        <td>100 commands per organization</td>
                        <td>1st of each month</td>
                    </tr>
                </tbody>
            </table>
            
            <div class="warning-box">
                <p>⚠️ <strong>AI Disclaimer:</strong> AI-generated content is provided for convenience only. AI outputs may contain 
                errors and should not be relied upon as professional, legal, financial, or medical advice. Always verify AI-generated 
                suggestions independently before making decisions.</p>
            </div>
        </div>
        
        <div class="card">
            <h2><span class="icon">©️</span> Intellectual Property</h2>
            <p>
                <strong>Our Ownership:</strong> Decision Agent, including its code, design, logos, and documentation, is owned by 
                Alphanimble Private Limited and is protected by intellectual property laws. You are granted a limited, non-exclusive, 
                non-transferable license to use the service in accordance with these Terms.
            </p>
            <p>
                <strong>Your Ownership:</strong> You retain ownership of all data and content you create using Decision Agent, 
                including decision proposals, votes, and configurations. By using the service, you grant us a limited license to 
                process and store your data as necessary to provide the service.
            </p>
        </div>
        
        <div class="card">
            <h2><span class="icon">📄</span> User Content & Data</h2>
            <p>You are solely responsible for the content you submit to Decision Agent. By submitting content, you represent that:</p>
            <ul>
                <li>You have the right to submit and share the content</li>
                <li>The content does not violate any laws or third-party rights</li>
                <li>The content is accurate and not misleading</li>
            </ul>
            <p>
                We may remove or disable access to content that violates these Terms or that we reasonably believe may create 
                liability for us or harm other users.
            </p>
        </div>
        
        <div class="card">
            <h2><span class="icon">⚡</span> Service Availability</h2>
            <p>
                We strive to maintain high availability, but we do not guarantee uninterrupted access to Decision Agent. 
                The service may be temporarily unavailable due to:
            </p>
            <ul>
                <li>Scheduled maintenance (we will attempt to provide advance notice when possible)</li>
                <li>Unscheduled maintenance or emergency repairs</li>
                <li>Third-party service outages (Slack, Zoho, cloud providers, AI services)</li>
                <li>Events beyond our reasonable control (force majeure)</li>
            </ul>
            <p>We are not liable for any damages resulting from service interruptions or unavailability.</p>
        </div>
        
        <div class="card">
            <h2><span class="icon">🚫</span> Termination</h2>
            <p><strong>Termination by You:</strong> You may stop using Decision Agent at any time by uninstalling the app from your Slack workspace.</p>
            <p><strong>Termination by Us:</strong> We reserve the right to suspend or terminate your access to Decision Agent if:</p>
            <ul>
                <li>You violate these Terms of Service</li>
                <li>You engage in abusive or harmful behavior</li>
                <li>We are required to do so by law</li>
                <li>We discontinue the service (with reasonable notice)</li>
            </ul>
            <p>
                Upon termination, your right to use the service will immediately cease. Data retention after termination 
                is governed by our Privacy Policy.
            </p>
        </div>
        
        <div class="card">
            <h2><span class="icon">⚠️</span> Disclaimers</h2>
            <p>
                <strong>DECISION AGENT IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EXPRESS OR IMPLIED.</strong>
            </p>
            <p>To the maximum extent permitted by law, we disclaim all warranties, including but not limited to:</p>
            <ul>
                <li>Implied warranties of merchantability and fitness for a particular purpose</li>
                <li>Warranties that the service will meet your requirements</li>
                <li>Warranties that the service will be uninterrupted, secure, or error-free</li>
                <li>Warranties regarding the accuracy or reliability of any information obtained through the service</li>
            </ul>
            <p>
                You use Decision Agent at your own risk. We are not responsible for decisions made based on information 
                or features provided by the service.
            </p>
        </div>
        
        <div class="card">
            <h2><span class="icon">💰</span> Limitation of Liability</h2>
            <p>To the maximum extent permitted by applicable law, in no event shall Alphanimble Private Limited be liable for any:</p>
            <ul>
                <li>Indirect, incidental, special, consequential, or punitive damages</li>
                <li>Loss of profits, data, business opportunities, or goodwill</li>
                <li>Damages resulting from unauthorized access to your data</li>
                <li>Damages exceeding the amount paid by you to us in the 12 months preceding the claim</li>
            </ul>
            <p>
                Some jurisdictions do not allow the exclusion of certain warranties or limitation of liability, 
                so the above limitations may not apply to you.
            </p>
        </div>
        
        <div class="card">
            <h2><span class="icon">🛡️</span> Indemnification</h2>
            <p>
                You agree to indemnify, defend, and hold harmless Alphanimble Private Limited and its officers, directors, 
                employees, and agents from any claims, damages, losses, liabilities, costs, and expenses (including 
                reasonable attorneys' fees) arising from:
            </p>
            <ul>
                <li>Your use of Decision Agent</li>
                <li>Your violation of these Terms</li>
                <li>Your violation of any third-party rights</li>
                <li>Content you submit through the service</li>
            </ul>
        </div>
        
        <div class="card">
            <h2><span class="icon">⚖️</span> Governing Law & Disputes</h2>
            <p>
                These Terms shall be governed by and construed in accordance with the laws of India, without regard to 
                its conflict of law provisions.
            </p>
            <p>Any disputes arising from these Terms or your use of Decision Agent shall be resolved through:</p>
            <ul>
                <li><strong>Informal Resolution:</strong> We encourage you to contact us first to resolve any issues amicably</li>
                <li><strong>Arbitration:</strong> If informal resolution fails, disputes shall be settled by binding arbitration</li>
                <li><strong>Jurisdiction:</strong> The courts of Bangalore, Karnataka, India shall have exclusive jurisdiction</li>
            </ul>
        </div>
        
        <div class="card">
            <h2><span class="icon">📝</span> Changes to These Terms</h2>
            <p>We may update these Terms from time to time. When we make significant changes:</p>
            <ul>
                <li>We will update the "Last Updated" date at the bottom of this page</li>
                <li>We will notify workspace admins via Slack or email for material changes</li>
                <li>We may require you to accept the updated Terms to continue using the service</li>
            </ul>
            <p>Continued use of Decision Agent after changes constitutes acceptance of the updated Terms.</p>
        </div>
        
        <div class="card">
            <h2><span class="icon">📌</span> General Provisions</h2>
            <ul>
                <li><strong>Entire Agreement:</strong> These Terms, together with our Privacy Policy, constitute the entire agreement between you and us</li>
                <li><strong>Severability:</strong> If any provision of these Terms is found unenforceable, the remaining provisions will remain in effect</li>
                <li><strong>No Waiver:</strong> Our failure to enforce any right or provision will not be considered a waiver of those rights</li>
                <li><strong>Assignment:</strong> You may not assign your rights under these Terms without our consent; we may assign our rights at any time</li>
            </ul>
        </div>
        
        <div class="contact-section">
            <h2><span class="icon">📧</span> Contact Us</h2>
            <p>
                If you have questions about these Terms of Service or need to contact us for any reason, please reach out:
            </p>
            <a href="mailto:info@alphanimble.com" class="contact-email">info@alphanimble.com</a>
            <p style="margin-top: 16px;">
                <strong>Alphanimble Private Limited</strong><br>
                Legal Inquiries
            </p>
        </div>
        
        <div class="footer">
            <p>Last updated: January 2026</p>
            <div class="footer-links">
                <a href="/privacy">Privacy Policy</a>
                <a href="/support">Support</a>
                <a href="/dashboard">Dashboard</a>
            </div>
        </div>
    </div>
    
    <script>
        // Dynamically set the back button URL with orgId if available
        (function() {
            var orgId = "{org_id}";
            
            if (!orgId || orgId === "") {
                var urlParams = new URLSearchParams(window.location.search);
                orgId = urlParams.get('orgId') || urlParams.get('org_id') || '';
            }
            
            var backButton = document.querySelector('.back-button');
            if (backButton && orgId && orgId !== "") {
                backButton.href = '/dashboard?orgId=' + encodeURIComponent(orgId);
            }
            
            var footerLinks = document.querySelectorAll('.footer-links a');
            footerLinks.forEach(function(link) {
                if (orgId && orgId !== "") {
                    var href = link.getAttribute('href');
                    if (href && !href.includes('orgId')) {
                        link.href = href + (href.includes('?') ? '&' : '?') + 'orgId=' + encodeURIComponent(orgId);
                    }
                }
            });
        })();
    </script>
</body>
</html>
"""


ZOHO_ERROR_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zoho Connection Error - Decision Agent</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 16px;
            padding: 48px;
            max-width: 500px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .emoji {
            font-size: 64px;
            margin-bottom: 24px;
        }
        
        h1 {
            color: #dc3545;
            font-size: 28px;
            margin-bottom: 16px;
        }
        
        p {
            color: #666;
            font-size: 16px;
            line-height: 1.6;
            margin-bottom: 24px;
        }
        
        .error-box {
            background: #fff5f5;
            border-left: 4px solid #dc3545;
            border-radius: 8px;
            padding: 20px;
            text-align: left;
            margin-bottom: 24px;
        }
        
        .error-box h3 {
            color: #dc3545;
            font-size: 14px;
            margin-bottom: 8px;
        }
        
        .error-box code {
            background: #ffe5e5;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            color: #721c24;
            display: block;
            margin-top: 8px;
            word-break: break-all;
        }
        
        .error-description {
            color: #555;
            font-size: 14px;
            line-height: 1.5;
        }
        
        .btn {
            display: inline-block;
            background: #667eea;
            color: white;
            text-decoration: none;
            padding: 14px 32px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 16px;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-right: 12px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #6c757d;
        }
        
        .btn-secondary:hover {
            box-shadow: 0 8px 24px rgba(108, 117, 125, 0.4);
        }
        
        .footer {
            margin-top: 24px;
            font-size: 12px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">❌</div>
        <h1>Connection Failed</h1>
        <p>
            We couldn't connect your Zoho CRM account.
            Please review the error below and try again.
        </p>
        
        <div class="error-box">
            <h3>Error Details:</h3>
            <p class="error-description">{error_description}</p>
            <code>{error}</code>
        </div>
        
        <div>
            <a href="/" class="btn">Try Again</a>
            <a href="/support" class="btn btn-secondary">Get Support</a>
        </div>
        
        <p class="footer">
            If this problem persists, please contact support@decisionagent.ai
        </p>
    </div>
</body>
</html>
"""
