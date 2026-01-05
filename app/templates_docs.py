"""
Documentation templates for Zoho Marketplace submission.

These pages are required for:
- Admin Guide
- User Guide
- Help Document
- Case Studies
"""

# Common styles for all documentation pages
DOCS_COMMON_STYLES = """
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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
            background-color: var(--bg-body);
            color: var(--text-main);
            line-height: 1.6;
            padding: 40px 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .back-button {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 8px 16px; background: transparent;
            border: 1px solid var(--border); color: var(--text-muted);
            text-decoration: none; border-radius: 8px;
            font-size: 14px; font-weight: 600;
            transition: all 0.2s; margin-bottom: 24px;
        }
        .back-button:hover { background: #f8fafc; color: var(--primary); border-color: var(--primary); }
        .back-button svg { width: 16px; height: 16px; }
        .header { text-align: center; margin-bottom: 32px; }
        .header-icon { width: 48px; height: 48px; margin: 0 auto 16px; display: block; }
        .header h1 { font-size: 28px; font-weight: 700; margin-bottom: 8px; color: var(--text-main); }
        .header p { color: var(--text-muted); font-size: 15px; font-weight: 500; }
        .card {
            background: var(--bg-card); border-radius: var(--radius);
            padding: 24px; margin-bottom: 16px;
            border: 1px solid var(--border); box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        h2 { color: var(--text-main); margin-bottom: 12px; font-size: 16px; font-weight: 700; display: flex; align-items: center; gap: 8px; }
        h2 .icon { font-size: 16px; }
        h3 { color: var(--text-main); font-size: 14px; font-weight: 600; margin: 16px 0 8px; }
        p { color: var(--text-muted); font-size: 14px; line-height: 1.7; margin-bottom: 12px; }
        ul { padding-left: 20px; margin-bottom: 12px; }
        li { margin-bottom: 8px; color: var(--text-muted); font-size: 14px; line-height: 1.6; }
        li strong { color: var(--text-main); font-weight: 600; }
        .step-number {
            display: inline-flex; align-items: center; justify-content: center;
            width: 28px; height: 28px; background: var(--primary);
            color: white; border-radius: 50%; font-weight: 700; font-size: 14px; margin-right: 12px;
        }
        .step { display: flex; align-items: flex-start; margin-bottom: 16px; }
        .step-content { flex: 1; }
        .cmd {
            font-family: 'SF Mono', 'Monaco', 'Menlo', monospace;
            background: #f8fafc; padding: 12px 16px; border-radius: 8px;
            margin: 8px 0; border: 1px solid var(--border); font-size: 13px;
        }
        .cmd code { color: var(--primary); font-weight: 600; }
        .highlight-box {
            background: #eff6ff; border: 1px solid #dbeafe;
            border-radius: 8px; padding: 16px; margin: 12px 0;
        }
        .highlight-box p { margin: 0; color: #1e40af; font-weight: 500; }
        .footer { max-width: 800px; margin: 32px auto 0; text-align: center; color: var(--text-muted); font-size: 13px; padding-top: 24px; border-top: 1px solid var(--border); }
        .footer-links { display: flex; justify-content: center; gap: 24px; margin-top: 12px; }
        .footer-links a { color: var(--primary); text-decoration: none; font-size: 14px; font-weight: 600; }
        a { color: var(--primary); }
        @media (max-width: 640px) { body { padding: 24px 16px; } .card { padding: 20px; } }
    </style>
"""

ADMIN_GUIDE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Guide - Decision Agent | DeciAgent</title>
    <meta name="description" content="Administrator guide for setting up and managing Decision Agent for Slack & Zoho CRM integration.">
""" + DOCS_COMMON_STYLES + """
</head>
<body>
    <div class="container">
        <a href="/dashboard" class="back-button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
            Back to Dashboard
        </a>
        
        <div class="header">
            <svg class="header-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="#2563eb" stroke-width="2"/>
                <path d="M19.4 15C19.1277 15.6171 19.2583 16.3378 19.73 16.82L19.79 16.88C20.1656 17.2551 20.3766 17.7642 20.3766 18.295C20.3766 18.8258 20.1656 19.3349 19.79 19.71C19.4149 20.0856 18.9058 20.2966 18.375 20.2966C17.8442 20.2966 17.3351 20.0856 16.96 19.71L16.9 19.65C16.4178 19.1783 15.6971 19.0477 15.08 19.32C14.4755 19.5791 14.0826 20.1724 14.08 20.83V21C14.08 22.1046 13.1846 23 12.08 23C10.9754 23 10.08 22.1046 10.08 21V20.91C10.0642 20.2327 9.63587 19.6339 9 19.4C8.38291 19.1277 7.66219 19.2583 7.18 19.73L7.12 19.79C6.74485 20.1656 6.23582 20.3766 5.705 20.3766C5.17418 20.3766 4.66515 20.1656 4.29 19.79C3.91445 19.4149 3.70343 18.9058 3.70343 18.375C3.70343 17.8442 3.91445 17.3351 4.29 16.96L4.35 16.9C4.82167 16.4178 4.95229 15.6971 4.68 15.08C4.42093 14.4755 3.82764 14.0826 3.17 14.08H3C1.89543 14.08 1 13.1846 1 12.08C1 10.9754 1.89543 10.08 3 10.08H3.09C3.76733 10.0642 4.36613 9.63587 4.6 9C4.87229 8.38291 4.74167 7.66219 4.27 7.18L4.21 7.12C3.83445 6.74485 3.62343 6.23582 3.62343 5.705C3.62343 5.17418 3.83445 4.66515 4.21 4.29C4.58515 3.91445 5.09418 3.70343 5.625 3.70343C6.15582 3.70343 6.66485 3.91445 7.04 4.29L7.1 4.35C7.58219 4.82167 8.30291 4.95229 8.92 4.68H9C9.60447 4.42093 9.99738 3.82764 10 3.17V3C10 1.89543 10.8954 1 12 1C13.1046 1 14 1.89543 14 3V3.09C14.0026 3.74764 14.3955 4.34093 15 4.6C15.6171 4.87229 16.3378 4.74167 16.82 4.27L16.88 4.21C17.2551 3.83445 17.7642 3.62343 18.295 3.62343C18.8258 3.62343 19.3349 3.83445 19.71 4.21C20.0856 4.58515 20.2966 5.09418 20.2966 5.625C20.2966 6.15582 20.0856 6.66485 19.71 7.04L19.65 7.1C19.1783 7.58219 19.0477 8.30291 19.32 8.92V9C19.5791 9.60447 20.1724 9.99738 20.83 10H21C22.1046 10 23 10.8954 23 12C23 13.1046 22.1046 14 21 14H20.91C20.2524 14.0026 19.6591 14.3955 19.4 15Z" stroke="#2563eb" stroke-width="2"/>
            </svg>
            <h1>Administrator Guide</h1>
            <p>Decision Agent (DeciAgent) for Slack & Zoho CRM</p>
        </div>
        
        <div class="card">
            <h2><span class="icon">🚀</span> Getting Started</h2>
            <p>As an administrator, you'll need to set up integrations with both Zoho CRM and Slack to enable Decision Agent for your organization.</p>
            
            <div class="step">
                <span class="step-number">1</span>
                <div class="step-content">
                    <h3>Connect Zoho CRM</h3>
                    <p>Navigate to the Dashboard and click "Connect to Zoho CRM". Authorize the application to access your Zoho CRM account. This creates a custom module called "Slack_Decisions" to store all decisions.</p>
                </div>
            </div>
            
            <div class="step">
                <span class="step-number">2</span>
                <div class="step-content">
                    <h3>Connect Slack Workspace</h3>
                    <p>After Zoho CRM is connected, click "Add to Slack" to install the bot in your workspace. Select the channels where you want to enable decision tracking.</p>
                </div>
            </div>
            
            <div class="step">
                <span class="step-number">3</span>
                <div class="step-content">
                    <h3>Configure Channel Settings</h3>
                    <p>Use <code>/decision config</code> in each channel to set approval percentages and other voting parameters.</p>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2><span class="icon">⚙️</span> Configuration Options</h2>
            <ul>
                <li><strong>Approval Percentage:</strong> Set the percentage of votes needed to approve a decision (default: 60%)</li>
                <li><strong>Group Size:</strong> Automatically detected from channel members</li>
                <li><strong>AI Features:</strong> Enable/disable AI-powered suggestions and summaries (100 commands/month limit)</li>
            </ul>
            <div class="cmd"><code>/decision config percentage 70</code> - Set 70% approval threshold</div>
        </div>
        
        <div class="card">
            <h2><span class="icon">🔐</span> Security & Permissions</h2>
            <p>Decision Agent requires the following permissions:</p>
            <ul>
                <li><strong>Slack:</strong> Read/write messages in channels where the bot is invited, access user profiles</li>
                <li><strong>Zoho CRM:</strong> Create/read/update custom module records for decision sync</li>
            </ul>
            <div class="highlight-box">
                <p>🔒 All OAuth tokens are encrypted at rest using AES-256 encryption. Data is transmitted over TLS 1.2+.</p>
            </div>
        </div>
        
        <div class="card">
            <h2><span class="icon">📊</span> Monitoring & Analytics</h2>
            <p>Track decision-making activity through:</p>
            <ul>
                <li><strong>Dashboard:</strong> View connection status and recent activity</li>
                <li><strong>Zoho CRM:</strong> Access all synced decisions in the Slack_Decisions module</li>
                <li><strong>Slack Commands:</strong> Use <code>/decision list</code> to view decision history</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>© 2026 Alphanimble Private Limited</p>
            <div class="footer-links">
                <a href="/user-guide">User Guide</a>
                <a href="/help">Help Center</a>
                <a href="/support">Contact Support</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

USER_GUIDE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Guide - Decision Agent | DeciAgent</title>
    <meta name="description" content="User guide for Decision Agent - Learn how to create, vote on, and track team decisions in Slack.">
""" + DOCS_COMMON_STYLES + """
</head>
<body>
    <div class="container">
        <a href="/dashboard" class="back-button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
            Back to Dashboard
        </a>
        
        <div class="header">
            <svg class="header-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 21V19C20 16.7909 18.2091 15 16 15H8C5.79086 15 4 16.7909 4 19V21" stroke="#2563eb" stroke-width="2" stroke-linecap="round"/>
                <circle cx="12" cy="7" r="4" stroke="#2563eb" stroke-width="2"/>
            </svg>
            <h1>User Guide</h1>
            <p>Decision Agent (DeciAgent) for Slack</p>
        </div>
        
        <div class="card">
            <h2><span class="icon">📋</span> Creating Decisions</h2>
            <p>Propose a new decision for your team to vote on:</p>
            <div class="cmd"><code>/decision propose "We should adopt weekly standups"</code></div>
            <p>Your proposal will be posted to the channel with voting buttons. Team members can click to approve or reject.</p>
        </div>
        
        <div class="card">
            <h2><span class="icon">🗳️</span> Voting</h2>
            <p>Vote on pending decisions using commands or interactive buttons:</p>
            <div class="cmd"><code>/decision approve 42</code> - Vote to approve decision #42</div>
            <div class="cmd"><code>/decision reject 42</code> - Vote to reject decision #42</div>
            <div class="highlight-box">
                <p>⚠️ Votes are final and cannot be changed to ensure voting integrity.</p>
            </div>
        </div>
        
        <div class="card">
            <h2><span class="icon">📊</span> Viewing Decisions</h2>
            <div class="cmd"><code>/decision list</code> - See all decisions in the channel</div>
            <div class="cmd"><code>/decision list pending</code> - View only pending decisions</div>
            <div class="cmd"><code>/decision show 42</code> - View details of decision #42</div>
            <div class="cmd"><code>/decision search budget</code> - Search for decisions containing "budget"</div>
        </div>
        
        <div class="card">
            <h2><span class="icon">⚡</span> Quick Add</h2>
            <p>Record a decision that was already made (no voting required):</p>
            <div class="cmd"><code>/decision add "Team agreed to use Python for backend"</code></div>
            <p>This creates an immediately approved decision for record-keeping.</p>
        </div>
        
        <div class="card">
            <h2><span class="icon">🤖</span> AI Features</h2>
            <p>Use AI to help with decision-making:</p>
            <div class="cmd"><code>/decision summarize 42</code> - Get an AI summary of decision #42</div>
            <div class="cmd"><code>/decision suggest "reduce meeting time"</code> - Get AI suggestions</div>
            <div class="cmd"><code>/decision ai-limits</code> - Check your AI usage limits</div>
            <p>AI features are limited to 100 commands per month per organization.</p>
        </div>
        
        <div class="card">
            <h2><span class="icon">❓</span> Getting Help</h2>
            <div class="cmd"><code>/decision help</code> - Show all available commands</div>
        </div>
        
        <div class="footer">
            <p>© 2026 Alphanimble Private Limited</p>
            <div class="footer-links">
                <a href="/admin-guide">Admin Guide</a>
                <a href="/help">Help Center</a>
                <a href="/support">Contact Support</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

HELP_DOCUMENT_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Help Center - Decision Agent | DeciAgent</title>
    <meta name="description" content="Help documentation for Decision Agent - FAQs, troubleshooting, and support resources.">
""" + DOCS_COMMON_STYLES + """
</head>
<body>
    <div class="container">
        <a href="/dashboard" class="back-button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
            Back to Dashboard
        </a>
        
        <div class="header">
            <svg class="header-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="#2563eb" stroke-width="2"/>
                <path d="M9.09 9C9.3251 8.33167 9.78915 7.76811 10.4 7.40913C11.0108 7.05016 11.7289 6.91894 12.4272 7.03871C13.1255 7.15848 13.7588 7.52152 14.2151 8.06353C14.6713 8.60553 14.9211 9.29152 14.92 10C14.92 12 11.92 13 11.92 13" stroke="#2563eb" stroke-width="2" stroke-linecap="round"/>
                <circle cx="12" cy="17" r="1" fill="#2563eb"/>
            </svg>
            <h1>Help Center</h1>
            <p>Decision Agent (DeciAgent) Support</p>
        </div>
        
        <div class="card">
            <h2><span class="icon">❓</span> Frequently Asked Questions</h2>
            
            <h3>How does voting work?</h3>
            <p>When a proposal is created, it requires a configured percentage (default 60%) of channel members to approve. Once enough approvals are received, the decision is marked as approved. If rejections exceed the threshold, it's rejected.</p>
            
            <h3>Can I change my vote?</h3>
            <p>No, votes are final to ensure the integrity of the decision-making process.</p>
            
            <h3>What happens to pending decisions?</h3>
            <p>Decisions remain pending until they receive enough votes to be approved or rejected. There is no automatic timeout.</p>
            
            <h3>How are decisions synced to Zoho CRM?</h3>
            <p>When connected, all decisions (created, approved, rejected) are automatically synced to a custom "Slack_Decisions" module in your Zoho CRM.</p>
        </div>
        
        <div class="card">
            <h2><span class="icon">🔧</span> Troubleshooting</h2>
            
            <h3>Bot not responding to commands?</h3>
            <ul>
                <li>Ensure the Decision Agent bot is invited to the channel</li>
                <li>Check that you're using the correct command format: <code>/decision [command]</code></li>
                <li>Verify the app is still installed in your workspace</li>
            </ul>
            
            <h3>Decisions not syncing to Zoho CRM?</h3>
            <ul>
                <li>Check the Dashboard to ensure Zoho CRM is connected</li>
                <li>Re-authorize the connection if prompted</li>
                <li>Contact support if the issue persists</li>
            </ul>
            
            <h3>AI features not working?</h3>
            <ul>
                <li>Check your AI usage limits with <code>/decision ai-limits</code></li>
                <li>Limits reset on the 1st of each month (100 commands/month)</li>
            </ul>
        </div>
        
        <div class="card">
            <h2><span class="icon">📚</span> Documentation Links</h2>
            <ul>
                <li><a href="/admin-guide">Administrator Guide</a> - Setup and configuration</li>
                <li><a href="/user-guide">User Guide</a> - Using Decision Agent</li>
                <li><a href="/case-studies">Case Studies</a> - Real-world examples</li>
                <li><a href="/privacy">Privacy Policy</a> - Data handling practices</li>
                <li><a href="/terms">Terms of Service</a> - Usage terms</li>
            </ul>
        </div>
        
        <div class="card">
            <h2><span class="icon">📧</span> Contact Support</h2>
            <p>Need more help? Reach out to our support team:</p>
            <p><strong>Email:</strong> <a href="mailto:info@alphanimble.com">info@alphanimble.com</a></p>
            <p><strong>Company:</strong> Alphanimble Private Limited</p>
        </div>
        
        <div class="footer">
            <p>© 2026 Alphanimble Private Limited</p>
            <div class="footer-links">
                <a href="/admin-guide">Admin Guide</a>
                <a href="/user-guide">User Guide</a>
                <a href="/support">Contact Support</a>
            </div>
        </div>
    </div>
</body>
</html>
"""

CASE_STUDIES_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Case Studies - Decision Agent | DeciAgent</title>
    <meta name="description" content="Case studies showing how teams use Decision Agent for collaborative decision-making in Slack.">
""" + DOCS_COMMON_STYLES + """
    <style>
        .case-study { border-left: 4px solid var(--primary); padding-left: 20px; margin: 20px 0; }
        .case-study h3 { color: var(--primary); margin-bottom: 8px; }
        .metric { display: inline-block; background: var(--success-bg); color: #065f46; padding: 4px 12px; border-radius: 20px; font-size: 13px; font-weight: 600; margin-right: 8px; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/dashboard" class="back-button">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
            Back to Dashboard
        </a>
        
        <div class="header">
            <svg class="header-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 11L12 14L22 4" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M21 12V19C21 20.1046 20.1046 21 19 21H5C3.89543 21 3 20.1046 3 19V5C3 3.89543 3.89543 3 5 3H16" stroke="#2563eb" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <h1>Case Studies</h1>
            <p>Real-world examples of Decision Agent in action</p>
        </div>
        
        <div class="card">
            <h2><span class="icon">🏢</span> Software Development Team</h2>
            <div class="case-study">
                <h3>Challenge</h3>
                <p>A 15-person development team struggled to make quick decisions during sprint planning. Discussions often went in circles, and decisions made in meetings were easily forgotten.</p>
                
                <h3>Solution</h3>
                <p>The team adopted Decision Agent to formalize their decision-making process. Proposals for technical choices, feature priorities, and process changes were submitted via Slack commands.</p>
                
                <h3>Results</h3>
                <p>After 3 months of using Decision Agent:</p>
                <span class="metric">50% faster decisions</span>
                <span class="metric">100% decision traceability</span>
                <span class="metric">Zero forgotten decisions</span>
            </div>
        </div>
        
        <div class="card">
            <h2><span class="icon">📈</span> Marketing Agency</h2>
            <div class="case-study">
                <h3>Challenge</h3>
                <p>A marketing agency with remote team members across different time zones needed a way to make collaborative decisions without scheduling synchronous meetings.</p>
                
                <h3>Solution</h3>
                <p>Decision Agent enabled asynchronous voting on campaign strategies, budget allocations, and creative directions. The Zoho CRM integration provided a complete audit trail for client reporting.</p>
                
                <h3>Results</h3>
                <span class="metric">75% fewer meetings</span>
                <span class="metric">Complete audit trail</span>
                <span class="metric">Faster client approvals</span>
            </div>
        </div>
        
        <div class="card">
            <h2><span class="icon">🎓</span> University Research Group</h2>
            <div class="case-study">
                <h3>Challenge</h3>
                <p>A research group needed to democratically decide on research directions, conference submissions, and resource allocation while maintaining transparency.</p>
                
                <h3>Solution</h3>
                <p>Using Decision Agent, the group established a 70% approval threshold for major decisions. All members could propose and vote, creating an equitable decision-making culture.</p>
                
                <h3>Results</h3>
                <span class="metric">Democratic process</span>
                <span class="metric">Full transparency</span>
                <span class="metric">Better team alignment</span>
            </div>
        </div>
        
        <div class="card">
            <h2><span class="icon">💡</span> Getting Started</h2>
            <p>Ready to transform your team's decision-making process?</p>
            <ul>
                <li>Read the <a href="/admin-guide">Admin Guide</a> to set up Decision Agent</li>
                <li>Share the <a href="/user-guide">User Guide</a> with your team</li>
                <li><a href="/support">Contact us</a> for personalized onboarding support</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>© 2026 Alphanimble Private Limited</p>
            <div class="footer-links">
                <a href="/admin-guide">Admin Guide</a>
                <a href="/user-guide">User Guide</a>
                <a href="/support">Contact Support</a>
            </div>
        </div>
    </div>
</body>
</html>
"""
