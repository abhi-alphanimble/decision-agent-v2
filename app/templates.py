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
    <title>Privacy Policy - Decision Agent</title>
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
            position: relative;
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
            margin-bottom: 24px;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
        }
        
        .lock-icon {
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
        
        h2 {
            color: var(--text-main);
            margin-top: 24px;
            margin-bottom: 12px;
            font-size: 18px;
            font-weight: 700;
        }
        
        h2:first-of-type {
            margin-top: 0;
        }
        
        p, ul {
            margin-bottom: 12px;
            color: var(--text-muted);
            font-size: 14px;
            line-height: 1.6;
        }
        
        ul {
            padding-left: 20px;
        }
        
        li {
            margin-bottom: 8px;
        }
        
        li strong {
            color: var(--text-main);
            font-weight: 600;
        }
        
        .section {
            margin-bottom: 20px;
        }
        
        .updated {
            text-align: center;
            color: var(--text-muted);
            font-size: 12px;
            margin-top: 32px;
            padding-top: 20px;
            border-top: 1px solid var(--border);
            font-weight: 500;
        }
        
        .contact-email {
            color: var(--primary);
            font-weight: 600;
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
            <svg class="lock-icon" viewBox="0 0 495 495" xmlns="http://www.w3.org/2000/svg">
                <g>
                    <path style="fill:#9BC9FF;" d="M180,107.5c0-37.22,30.28-67.5,67.5-67.5S315,70.28,315,107.5V175h40v-67.5
                        C355,48.224,306.776,0,247.5,0S140,48.224,140,107.5V175h40V107.5z"/>
                    <path style="fill:#003F8A;" d="M247.5,175v96.431c22.056,0,40,17.944,40,40c0,14.773-8.056,27.691-20,34.619v50.566h-20V495H425
                        V175H247.5z"/>
                    <path style="fill:#2488FF;" d="M227.5,396.616V346.05c-11.944-6.927-20-19.846-20-34.619c0-22.056,17.944-40,40-40V175H70v320
                        h177.5v-98.384H227.5z"/>
                    <path style="fill:#BDDBFF;" d="M207.5,311.431c0,14.773,8.056,27.692,20,34.619v50.566h40V346.05c11.944-6.927,20-19.846,20-34.619
                        c0-22.056-17.944-40-40-40C225.444,271.431,207.5,289.375,207.5,311.431z"/>
                </g>
            </svg>
            <h1>Privacy Policy</h1>
            <p>Decision Agent for Slack</p>
        </div>
        
        <div class="section">
            <h2>Introduction</h2>
            <p>
                Decision Agent ("we", "our", or "the app") is a Slack application that helps teams 
                make group decisions through a voting system. This privacy policy explains what 
                information we collect, how we use it, and your rights regarding your data.
            </p>
        </div>
        
        <div class="section">
            <h2>Information We Collect</h2>
            <p>When you use Decision Agent, we collect and store:</p>
            <ul>
                <li><strong>Slack Workspace Information:</strong> Team ID, team name, and bot access tokens for API communication</li>
                <li><strong>Decision Data:</strong> Proposals submitted by users, including the text, proposer name, and channel</li>
                <li><strong>Voting Data:</strong> Votes cast on decisions, including voter name and vote type (approve/reject)</li>
                <li><strong>Channel Configuration:</strong> Custom settings like approval percentages</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>How We Use Your Information</h2>
            <p>We use the collected information to:</p>
            <ul>
                <li>Provide the decision-making functionality within your Slack workspace</li>
                <li>Track and display voting progress on decisions</li>
                <li>Send notifications about decision outcomes to relevant channels</li>
                <li>Sync decision data with connected integrations (e.g., Zoho CRM) if enabled</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>Data Storage &amp; Security</h2>
            <p>
                Your data is stored securely in our database. Access tokens are encrypted at rest 
                using industry-standard encryption (Fernet/AES). We implement appropriate technical 
                and organizational measures to protect your data.
            </p>
        </div>
        
        <div class="section">
            <h2>Data Sharing</h2>
            <p>
                We do not sell your data. We may share data with:
            </p>
            <ul>
                <li>Third-party integrations you explicitly enable (e.g., Zoho CRM sync)</li>
                <li>Service providers who help us operate the app (hosting, databases)</li>
                <li>Legal authorities if required by law</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>Data Retention</h2>
            <p>
                We retain your data for as long as the app is installed in your workspace. 
                When you uninstall the app, we remove your workspace tokens. Decision history 
                may be retained for audit purposes unless you request deletion.
            </p>
        </div>
        
        <div class="section">
            <h2>Your Rights</h2>
            <p>You have the right to:</p>
            <ul>
                <li>Access the data we hold about your workspace</li>
                <li>Request correction of inaccurate data</li>
                <li>Request deletion of your data</li>
                <li>Uninstall the app at any time from Slack</li>
            </ul>
        </div>
        
        <div class="section">
            <h2>Contact Us</h2>
            <p>
                If you have questions about this privacy policy or want to exercise your rights, 
                please contact us at: <span class="contact-email">info@alphanimble.com</span>
            </p>
        </div>
        
        <p class="updated">Last updated: December 2024</p>
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
