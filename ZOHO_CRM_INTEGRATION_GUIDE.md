# Zoho CRM Integration Guide - Decision Agent

## Overview
This guide provides step-by-step instructions to integrate the Decision Agent Slack bot with Zoho CRM. The integration will sync decision data (proposals, votes, status) from Slack to a custom Zoho CRM module in real-time.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Part 1: Zoho CRM Setup](#part-1-zoho-crm-setup)
3. [Part 2: Zoho API Configuration](#part-2-zoho-api-configuration)
4. [Part 3: Decision Agent Code Integration](#part-3-decision-agent-code-integration)
5. [Part 4: Testing & Validation](#part-4-testing--validation)
6. [Part 5: Production Deployment](#part-5-production-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Zoho CRM Requirements
- Active Zoho CRM account (Professional, Enterprise, or Ultimate plan)
- Administrator access to create custom modules
- API access enabled for your organization

### Decision Agent Requirements
- Python 3.11+ installed
- Current Decision Agent project running successfully
- Database access (PostgreSQL)
- Basic understanding of REST APIs

### Tools Needed
- Text editor (VS Code recommended)
- Postman or similar API testing tool (optional)
- Git for version control

---

## Part 1: Zoho CRM Setup

### Step 1.1: Create Custom Module "Decisions"

1. **Log in to Zoho CRM**
   - Navigate to: `Settings` → `Customization` → `Modules and Fields`

2. **Create New Module**
   - Click `+ New Module`
   - Module Name: `Decisions`
   - Singular Label: `Decision`
   - Plural Label: `Decisions`
   - Module Icon: Choose appropriate icon (e.g., clipboard or checkmark)
   - Click `Create`

### Step 1.2: Configure Module Fields

Create the following custom fields in the `Decisions` module:

| Field Label | Field Type | API Name | Properties | Required |
|------------|-----------|----------|-----------|----------|
| Decision ID | Number | `Decision_ID` | Unique, Auto-number disabled | Yes |
| Proposal Text | Multi Line | `Proposal_Text` | Max length: 1000 chars | Yes |
| Proposed By | Single Line | `Proposed_By` | Max length: 255 chars | Yes |
| Proposer Name | Single Line | `Proposer_Name` | Max length: 255 chars | Yes |
| Total Votes | Number | `Total_Votes` | Decimal places: 0 | Yes |
| Approve Votes | Number | `Approve_Votes` | Decimal places: 0 | Yes |
| Reject Votes | Number | `Reject_Votes` | Decimal places: 0 | Yes |
| Decision Status | Picklist | `Decision_Status` | Options: Pending, Approved, Rejected, Expired | Yes |
| Channel ID | Single Line | `Channel_ID` | Max length: 100 chars | Yes |
| Channel Name | Single Line | `Channel_Name` | Max length: 255 chars | No |
| Approval Threshold | Number | `Approval_Threshold` | Decimal places: 0 | Yes |
| Group Size | Number | `Group_Size` | Decimal places: 0 | Yes |
| Created At | DateTime | `Created_At` | Date format: DD-MM-YYYY HH:MM | Yes |
| Closed At | DateTime | `Closed_At` | Date format: DD-MM-YYYY HH:MM | No |

**Steps to Add Each Field:**
1. In the `Decisions` module settings, click `+ Add Field`
2. Select the field type from the list above
3. Enter the Field Label and API Name
4. Configure properties (max length, decimal places, picklist values, etc.)
5. Mark as Required or Optional
6. Click `Done`
7. Repeat for all fields

### Step 1.3: Configure Module Layout

1. **Organize Fields into Sections**
   - Go to: `Settings` → `Customization` → `Modules and Fields` → `Decisions` → `Layout`
   - Create sections:
     - **Decision Information**: Decision ID, Proposal Text, Decision Status
     - **Proposer Details**: Proposed By, Proposer Name
     - **Voting Details**: Total Votes, Approve Votes, Reject Votes, Approval Threshold
     - **Channel Information**: Channel ID, Channel Name, Group Size
     - **Timestamps**: Created At, Closed At

2. **Set Default View**
   - Configure list view to show: Decision ID, Proposal Text, Decision Status, Total Votes, Created At

### Step 1.4: Set Module Permissions

1. Navigate to: `Settings` → `Security Control` → `Profiles`
2. For each profile (Administrator, Standard, etc.):
   - Enable `Decisions` module access
   - Set permissions:
     - View: Yes
     - Create: Yes (for API integration)
     - Edit: Yes (for vote updates)
     - Delete: No (preserve data)

---

## Part 2: Zoho API Configuration

### Step 2.1: Register API Client

1. **Go to Zoho API Console**
   - Visit: https://api-console.zoho.com/
   - Sign in with your Zoho account

2. **Create Server-Based Application**
   - Click `ADD CLIENT`
   - Select `Server-based Applications`
   - Fill in details:
     - Client Name: `Decision Agent Integration`
     - Homepage URL: Your application URL (e.g., `https://yourdomain.com` or `http://localhost:8000`)
     - Authorized Redirect URIs: `http://localhost:8000/oauth/zoho/callback` (for testing)
   - Click `CREATE`

3. **Save Credentials**
   - Copy and save securely:
     - **Client ID**: `1000.XXXXXXXXXXXXXXXXXXXXXXXX`
     - **Client Secret**: `XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`
   - You'll need these for authentication

### Step 2.2: Generate Access Token

**Option A: Using OAuth 2.0 (Recommended for Production)**

1. **Generate Authorization Code**
   - Construct the URL (replace placeholders):
   ```
   https://accounts.zoho.com/oauth/v2/auth?scope=ZohoCRM.modules.ALL&client_id=YOUR_CLIENT_ID&response_type=code&access_type=offline&redirect_uri=http://localhost:8000/oauth/zoho/callback
   ```
   - Open URL in browser
   - Authorize the application
   - Copy the `code` parameter from the redirect URL

2. **Exchange Code for Tokens**
   - Use this curl command (replace placeholders):
   ```bash
   curl -X POST https://accounts.zoho.com/oauth/v2/token \
     -d "code=YOUR_AUTHORIZATION_CODE" \
     -d "client_id=YOUR_CLIENT_ID" \
     -d "client_secret=YOUR_CLIENT_SECRET" \
     -d "redirect_uri=http://localhost:8000/oauth/zoho/callback" \
     -d "grant_type=authorization_code"
   ```

3. **Save Response**
   - You'll receive:
     - `access_token`: Valid for 1 hour
     - `refresh_token`: Use to generate new access tokens
     - `expires_in`: Token expiry time (3600 seconds)

**Option B: Using Self-Client (Development Only)**

1. Navigate to: `Settings` → `Customization` → `API` → `OAuth`
2. Enable `Self Client`
3. Generate token with required scopes: `ZohoCRM.modules.ALL`
4. Copy the generated token

### Step 2.3: Test API Connection

Use Postman or curl to verify API access:

```bash
curl -X GET "https://www.zohoapis.com/crm/v3/Decisions" \
  -H "Authorization: Zoho-oauthtoken YOUR_ACCESS_TOKEN"
```

Expected response: Empty list `[]` (module is empty initially)

---

## Part 3: Decision Agent Code Integration

### Step 3.1: Project Structure Setup

Create the following new files and directories:

```
decision-agent-v2/
├── app/
│   ├── integrations/          # NEW: Create this directory
│   │   ├── __init__.py
│   │   ├── zoho_crm.py        # Zoho CRM client
│   │   └── zoho_sync.py       # Sync logic
│   └── ...
├── .env                        # Add Zoho credentials here
└── ZOHO_CRM_INTEGRATION_GUIDE.md  # This file
```

### Step 3.2: Environment Configuration

Add the following to your `.env` file:

```bash
# Zoho CRM Configuration
ZOHO_CLIENT_ID=1000.XXXXXXXXXXXXXXXXXXXXXXXX
ZOHO_CLIENT_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ZOHO_REFRESH_TOKEN=1000.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ZOHO_API_DOMAIN=https://www.zohoapis.com  # or .eu, .in, .com.au based on your data center
ZOHO_ACCOUNTS_URL=https://accounts.zoho.com  # or .eu, .in, .com.au
ZOHO_ENABLED=true  # Set to false to disable Zoho sync
```

### Step 3.3: Install Required Dependencies

Add to `requirements.txt`:

```txt
requests>=2.31.0
python-dotenv>=1.0.0  # If not already present
```

Install:
```bash
pip install requests python-dotenv
```

### Step 3.4: Implementation Files to Create

#### File 1: `app/integrations/__init__.py`
```python
"""Integrations package for external services"""
```

#### File 2: `app/integrations/zoho_crm.py`
Create a Zoho CRM client class with methods:
- `__init__()`: Initialize with credentials
- `get_access_token()`: Refresh access token using refresh_token
- `create_decision(decision_data)`: Create new decision record in Zoho
- `update_decision(decision_id, update_data)`: Update existing decision
- `get_decision_by_id(decision_id)`: Fetch decision from Zoho
- `_make_request(method, endpoint, data)`: Generic API request handler

#### File 3: `app/integrations/zoho_sync.py`
Create sync functions:
- `sync_decision_to_zoho(decision)`: Sync decision after creation
- `sync_vote_to_zoho(decision_id, vote)`: Update vote counts after vote
- `is_zoho_enabled()`: Check if Zoho integration is enabled
- `handle_zoho_sync_error(error)`: Error handling and logging

### Step 3.5: Integration Points

**Modify these existing files to call Zoho sync:**

1. **`app/handlers/decision_handlers.py`**
   - In `handle_propose_command()`: After creating decision, call `sync_decision_to_zoho()`
   - In `handle_approve_command()`: After vote, call `sync_vote_to_zoho()`
   - In `handle_reject_command()`: After vote, call `sync_vote_to_zoho()`
   - In `handle_add_command()`: After creating pre-approved decision, call `sync_decision_to_zoho()`

2. **`app/jobs/auto_close.py`**
   - In auto-close logic: After closing decision, call `sync_vote_to_zoho()` to update status

**Example integration pattern:**
```python
# After creating decision
decision = crud.create_decision(...)
logger.info(f"✅ Created decision #{decision.id}")

# Sync to Zoho CRM
if is_zoho_enabled():
    try:
        sync_decision_to_zoho(decision)
        logger.info(f"✅ Synced decision #{decision.id} to Zoho CRM")
    except Exception as e:
        logger.error(f"❌ Failed to sync to Zoho: {e}")
        # Continue execution - don't fail the main operation
```

### Step 3.6: Data Mapping

Map Decision Agent data to Zoho CRM fields:

| Decision Agent Field | Zoho CRM Field | Transformation |
|---------------------|----------------|----------------|
| `decision.id` | `Decision_ID` | Direct mapping |
| `decision.text` | `Proposal_Text` | Direct mapping |
| `decision.proposer_phone` | `Proposed_By` | Direct mapping |
| `decision.proposer_name` | `Proposer_Name` | Direct mapping |
| `decision.approval_count + decision.rejection_count` | `Total_Votes` | Calculate sum |
| `decision.approval_count` | `Approve_Votes` | Direct mapping |
| `decision.rejection_count` | `Reject_Votes` | Direct mapping |
| `decision.status` | `Decision_Status` | Map: pending→Pending, approved→Approved, rejected→Rejected, expired→Expired |
| `decision.channel_id` | `Channel_ID` | Direct mapping |
| Get from Slack API | `Channel_Name` | Fetch using `slack_client.get_channel_info()` |
| `decision.approval_threshold` | `Approval_Threshold` | Direct mapping |
| `decision.group_size_at_creation` | `Group_Size` | Direct mapping |
| `decision.created_at` | `Created_At` | Convert to ISO format: `YYYY-MM-DDTHH:MM:SS+00:00` |
| `decision.closed_at` | `Closed_At` | Convert to ISO format (if not None) |

---

## Part 4: Testing & Validation

### Step 4.1: Unit Testing

Create test file: `tests/test_zoho_integration.py`

Test scenarios:
1. **Test access token refresh**
   - Verify token is refreshed when expired
   - Verify token is cached and reused

2. **Test decision creation**
   - Create a test decision in Decision Agent
   - Verify it appears in Zoho CRM with correct data

3. **Test vote updates**
   - Cast approve/reject votes
   - Verify vote counts update in Zoho CRM

4. **Test status changes**
   - Auto-close a decision
   - Verify status updates to "Expired" in Zoho

5. **Test error handling**
   - Simulate API failures
   - Verify errors are logged and don't break main flow

### Step 4.2: Manual Testing Checklist

- [ ] Environment variables loaded correctly
- [ ] Zoho OAuth token refresh works
- [ ] Create decision in Slack → appears in Zoho CRM
- [ ] Approve vote in Slack → vote count updates in Zoho
- [ ] Reject vote in Slack → vote count updates in Zoho
- [ ] Decision auto-closes → status updates in Zoho
- [ ] Pre-approved decision (`/decision add`) → appears in Zoho
- [ ] Channel name fetched and displayed correctly
- [ ] Timestamps in correct timezone
- [ ] Error handling doesn't crash the bot

### Step 4.3: Load Testing

Test with multiple decisions:
1. Create 10 decisions quickly
2. Cast 50 votes across decisions
3. Verify all sync without delays or failures
4. Check Zoho API rate limits (5000 requests/day for CRM Plus)

---

## Part 5: Production Deployment

### Step 5.1: Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables set in production
- [ ] Zoho OAuth tokens generated for production
- [ ] Logging configured for Zoho sync events
- [ ] Error monitoring setup (e.g., Sentry)
- [ ] Database backup taken
- [ ] Rollback plan documented

### Step 5.2: Deployment Steps

1. **Update Environment Variables**
   ```bash
   # On production server
   export ZOHO_CLIENT_ID=production_client_id
   export ZOHO_CLIENT_SECRET=production_secret
   export ZOHO_REFRESH_TOKEN=production_refresh_token
   export ZOHO_ENABLED=true
   ```

2. **Deploy Code**
   ```bash
   git pull origin main
   pip install -r requirements.txt
   python -m alembic upgrade head  # If any DB migrations
   ```

3. **Restart Server**
   ```bash
   # Using systemd
   sudo systemctl restart decision-agent

   # Or using PM2
   pm2 restart decision-agent

   # Or direct
   python run.py
   ```

4. **Verify Integration**
   - Check logs for "✅ Synced decision to Zoho CRM"
   - Create test decision and verify in Zoho
   - Monitor for errors in first hour

### Step 5.3: Monitoring & Maintenance

1. **Log Monitoring**
   - Track sync success/failure rates
   - Monitor API response times
   - Alert on repeated failures

2. **Token Refresh Schedule**
   - Access tokens expire in 1 hour
   - Implement automatic refresh before expiry
   - Monitor refresh token validity (expires after 90 days of inactivity)

3. **Performance Metrics**
   - Track sync latency (should be < 2 seconds)
   - Monitor Zoho API usage against quota
   - Set up alerts for quota threshold (e.g., 80% of daily limit)

---

## Troubleshooting

### Issue 1: Authentication Errors

**Symptom:** `401 Unauthorized` or `Invalid token`

**Solutions:**
1. Verify credentials in `.env` are correct
2. Check if refresh token has expired (generate new one)
3. Verify API scopes include `ZohoCRM.modules.ALL`
4. Ensure correct Zoho data center domain (`.com`, `.eu`, `.in`, `.com.au`)

### Issue 2: Module Not Found

**Symptom:** `404 Not Found` when accessing Decisions module

**Solutions:**
1. Verify module name is exactly `Decisions` (case-sensitive)
2. Check module is visible to the API profile
3. Verify API permissions for the module
4. Check if module was created in correct Zoho account

### Issue 3: Field Mapping Errors

**Symptom:** `Invalid field` or `Missing required field` errors

**Solutions:**
1. Verify all required fields exist in Zoho module
2. Check API names match exactly (case-sensitive)
3. Verify field types match (Number, DateTime, etc.)
4. Check field validation rules in Zoho

### Issue 4: Rate Limit Exceeded

**Symptom:** `429 Too Many Requests`

**Solutions:**
1. Implement exponential backoff retry logic
2. Batch multiple updates if possible
3. Cache data to reduce duplicate API calls
4. Consider upgrading Zoho plan for higher limits

### Issue 5: Sync Delays

**Symptom:** Data appears in Zoho with significant delay

**Solutions:**
1. Make sync async (use background tasks)
2. Implement retry queue for failed syncs
3. Check network latency to Zoho servers
4. Optimize data payload size

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Slack Workspace                          │
│  ┌────────────────┐      ┌────────────────┐                    │
│  │   User creates │─────▶│  User votes on │                    │
│  │    decision    │      │    decision    │                    │
│  └────────────────┘      └────────────────┘                    │
└───────────────┬─────────────────┬───────────────────────────────┘
                │                 │
                ▼                 ▼
        ┌───────────────────────────────────┐
        │     Decision Agent (FastAPI)      │
        │  ┌─────────────────────────────┐  │
        │  │  Decision Handlers          │  │
        │  │  - handle_propose_command() │  │
        │  │  - handle_approve_command() │  │
        │  │  - handle_reject_command()  │  │
        │  └──────────┬──────────────────┘  │
        │             │                      │
        │  ┌──────────▼──────────────────┐  │
        │  │  Zoho Sync Service          │  │
        │  │  - sync_decision_to_zoho()  │  │
        │  │  - sync_vote_to_zoho()      │  │
        │  └──────────┬──────────────────┘  │
        └─────────────┼───────────────────┘
                      │
                      ▼
        ┌───────────────────────────────┐
        │       Zoho CRM Client         │
        │  - OAuth Token Management     │
        │  - API Request Handler        │
        │  - Error Handling & Retry     │
        └──────────┬────────────────────┘
                   │
                   ▼ HTTPS/REST API
        ┌───────────────────────────────┐
        │         Zoho CRM API          │
        │  ┌─────────────────────────┐  │
        │  │  Custom Module:         │  │
        │  │    "Decisions"          │  │
        │  │  - Decision ID          │  │
        │  │  - Proposal Text        │  │
        │  │  - Vote Counts          │  │
        │  │  - Status               │  │
        │  └─────────────────────────┘  │
        └───────────────────────────────┘
```

---

## Security Best Practices

1. **Never commit credentials to Git**
   - Use `.env` file (already in `.gitignore`)
   - Use environment variables in production

2. **Rotate tokens regularly**
   - Refresh tokens every 30-60 days
   - Monitor for unauthorized access

3. **Use HTTPS only**
   - All API calls must use HTTPS
   - Verify SSL certificates

4. **Implement rate limiting**
   - Respect Zoho API quotas
   - Implement exponential backoff

5. **Audit logging**
   - Log all sync operations
   - Track who/what/when for compliance

---

## Next Steps After Integration

1. **Add Webhooks (Optional)**
   - Listen for Zoho CRM updates
   - Sync changes back to Slack (two-way sync)

2. **Dashboard & Reports**
   - Create Zoho Analytics dashboards
   - Track decision metrics over time

3. **Additional Modules**
   - Create "Voters" module to track individual votes
   - Link decisions to Contacts/Leads in CRM

4. **Automated Workflows**
   - Set up Zoho workflow rules
   - Auto-assign decisions to sales reps
   - Send email notifications on status changes

---

## Support & Resources

- **Zoho CRM API Documentation**: https://www.zoho.com/crm/developer/docs/api/v3/
- **Zoho OAuth Documentation**: https://www.zoho.com/accounts/protocol/oauth.html
- **Decision Agent Repository**: https://github.com/abhi-alphanimble/decision-agent-v2
- **Postman Collection**: (Create and share for API testing)

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-08 | 1.0.0 | Initial integration guide created |

---

**Document prepared by:** Decision Agent Development Team  
**Last updated:** December 8, 2025  
**Status:** Ready for implementation
