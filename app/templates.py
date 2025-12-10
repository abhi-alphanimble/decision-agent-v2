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
            Need help? Contact us at support@example.com
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
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f8f9fa;
            color: #333;
            line-height: 1.8;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 48px 20px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 32px;
            margin-bottom: 8px;
        }
        
        .header p {
            opacity: 0.9;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 48px 20px;
        }
        
        h2 {
            color: #1a1a2e;
            margin-top: 32px;
            margin-bottom: 16px;
            font-size: 22px;
        }
        
        p, ul {
            margin-bottom: 16px;
            color: #555;
        }
        
        ul {
            padding-left: 24px;
        }
        
        li {
            margin-bottom: 8px;
        }
        
        .section {
            background: white;
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .updated {
            text-align: center;
            color: #999;
            font-size: 14px;
            margin-top: 48px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 Privacy Policy</h1>
        <p>Decision Agent for Slack</p>
    </div>
    
    <div class="container">
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
                <li><strong>Channel Configuration:</strong> Custom settings like approval percentages and timeout periods</li>
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
            <h2>Data Storage & Security</h2>
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
                please contact us at: <strong>support@example.com</strong>
            </p>
        </div>
        
        <p class="updated">Last updated: December 2024</p>
    </div>
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
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f8f9fa;
            color: #333;
            line-height: 1.8;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 48px 20px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 32px;
            margin-bottom: 8px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 48px 20px;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        h2 {
            color: #1a1a2e;
            margin-bottom: 16px;
            font-size: 22px;
        }
        
        h3 {
            color: #667eea;
            margin-top: 24px;
            margin-bottom: 12px;
        }
        
        p {
            color: #555;
            margin-bottom: 16px;
        }
        
        .command-list {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 16px 0;
        }
        
        .cmd {
            font-family: 'Monaco', 'Menlo', monospace;
            background: #e9ecef;
            padding: 10px 14px;
            border-radius: 6px;
            margin-bottom: 12px;
            display: flex;
            align-items: flex-start;
        }
        
        .cmd:last-child {
            margin-bottom: 0;
        }
        
        .cmd code {
            font-weight: 600;
            color: #667eea;
            min-width: 250px;
        }
        
        .cmd span {
            color: #666;
            font-family: inherit;
        }
        
        .contact-card {
            text-align: center;
            padding: 40px;
        }
        
        .contact-card .emoji {
            font-size: 48px;
            margin-bottom: 16px;
        }
        
        .email-link {
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            font-size: 18px;
        }
        
        .email-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>💬 Support</h1>
        <p>Decision Agent for Slack</p>
    </div>
    
    <div class="container">
        <div class="card">
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
        
        <div class="card">
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
                Decisions automatically expire after 48 hours (configurable per channel). 
                Expired decisions are marked with an expired status.
            </p>
            
            <h3>How do I change the approval percentage?</h3>
            <p>
                Use <code>/decision config percentage 70</code> to set the required approval 
                percentage to 70% for the current channel.
            </p>
        </div>
        
        <div class="card contact-card">
            <div class="emoji">📧</div>
            <h2>Need More Help?</h2>
            <p>Contact our support team:</p>
            <a href="mailto:support@example.com" class="email-link">support@example.com</a>
        </div>
    </div>
</body>
</html>
"""
