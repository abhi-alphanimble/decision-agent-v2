# Zoho Marketplace Multi-Tenant Implementation Plan

This document outlines the complete implementation plan for making the Decision Agent support multi-tenant Zoho CRM integration, enabling publication on the Zoho Marketplace.

---

## Overview

### Current State
- Single Zoho CRM credentials in `.env`
- All decisions from all Slack workspaces sync to ONE Zoho CRM account
- Not suitable for distribution

### Target State
- Each Slack workspace connects to their OWN Zoho CRM account
- Data isolation: Org A's decisions → Org A's Zoho only
- Ready for Zoho Marketplace distribution

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Decision Agent                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐         ┌─────────────────┐               │
│  │ Slack Workspace │         │ Zoho CRM        │               │
│  │ (Team ID: T123) │ ──────► │ (Org A)         │               │
│  └─────────────────┘         └─────────────────┘               │
│          │                           │                          │
│          │     ┌─────────────┐       │                          │
│          └────►│  Database   │◄──────┘                          │
│                │             │                                   │
│                │ - slack_installations (team_id, token)         │
│                │ - zoho_installations (team_id, refresh_token)  │
│                │ - decisions (team_id, ...)                     │
│                └─────────────┘                                   │
│                       │                                          │
│  ┌─────────────────┐  │      ┌─────────────────┐               │
│  │ Slack Workspace │  │      │ Zoho CRM        │               │
│  │ (Team ID: T456) │──┴─────►│ (Org B)         │               │
│  └─────────────────┘         └─────────────────┘               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Database Changes

### 1.1 Create `zoho_installations` Table

**Purpose:** Store Zoho OAuth credentials per Slack team

**Schema:**
```sql
CREATE TABLE zoho_installations (
    id SERIAL PRIMARY KEY,
    team_id VARCHAR(50) UNIQUE NOT NULL,      -- Links to slack_installations.team_id
    zoho_org_id VARCHAR(100),                  -- Zoho organization ID
    zoho_domain VARCHAR(50) NOT NULL,          -- e.g., 'com', 'in', 'eu'
    access_token TEXT NOT NULL,                -- Encrypted
    refresh_token TEXT NOT NULL,               -- Encrypted
    token_expires_at TIMESTAMP,
    installed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    installed_by VARCHAR(100),                 -- User who connected
    FOREIGN KEY (team_id) REFERENCES slack_installations(team_id) ON DELETE CASCADE
);
```

**Files to Modify:**
- `app/models.py` - Add `ZohoInstallation` model
- `alembic/versions/` - Create migration

### 1.2 Add `team_id` to Decisions Table (if not present)

**Purpose:** Track which Slack team created each decision

**Check:** Verify if `decisions` table already has `team_id` column. If not, add it.

---

## Phase 2: Zoho OAuth Flow

### 2.1 Register Zoho OAuth Client

**Location:** https://api-console.zoho.com/

**Steps:**
1. Create a "Server-based Application"
2. Set redirect URI: `https://your-domain.ngrok-free.dev/zoho/install/callback`
3. Note down: Client ID, Client Secret
4. Required scopes:
   - `ZohoCRM.modules.ALL`
   - `ZohoCRM.settings.ALL`
   - `ZohoCRM.org.READ`

### 2.2 Create OAuth Endpoints

**File:** `app/main.py` (or new `app/integrations/zoho_oauth.py`)

**Endpoints:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/zoho/install` | GET | Redirect to Zoho OAuth (requires `team_id` param) |
| `/zoho/install/callback` | GET | Exchange code for tokens, store in DB |
| `/zoho/status` | GET | Check if Zoho is connected for a team |
| `/zoho/disconnect` | POST | Remove Zoho connection for a team |

**Flow:**
```
User clicks "Connect Zoho" in Slack (or web page)
    ↓
GET /zoho/install?team_id=T123
    ↓
Redirect to Zoho OAuth consent page
    ↓
User approves → Zoho redirects to /zoho/install/callback?code=xxx&state=T123
    ↓
Exchange code for access_token + refresh_token
    ↓
Encrypt and store tokens in zoho_installations table
    ↓
Show success page
```

### 2.3 State Parameter for Security

**Purpose:** Prevent CSRF attacks, carry `team_id` through OAuth

**Implementation:**
- Generate state: `base64(team_id + random_nonce)`
- Store nonce in session/cache temporarily
- Verify on callback

---

## Phase 3: Modify Sync Logic

### 3.1 Update `ZohoCRMClient`

**File:** `app/integrations/zoho_crm.py`

**Changes:**
- Remove global credentials from `__init__`
- Accept `team_id` parameter
- Fetch credentials from `zoho_installations` table
- Decrypt tokens before use

**New Constructor:**
```python
def __init__(self, team_id: str, db: Session):
    self.team_id = team_id
    # Fetch credentials from DB
    # Decrypt tokens
    # Initialize client
```

### 3.2 Update `zoho_sync.py`

**File:** `app/integrations/zoho_sync.py`

**Changes:**
- Add `team_id` parameter to all sync functions
- Create `ZohoCRMClient` instance per call using team's credentials
- Handle case where team has no Zoho connection (skip sync)

**Functions to Update:**
- `sync_decision_to_zoho(decision, team_id, db)`
- `sync_vote_to_zoho(decision, channel_name, team_id, db)`

### 3.3 Pass `team_id` Through Decision Flow

**Files to Update:**
- `app/handlers/decision_handlers.py` - Pass `team_id` to sync functions
- `app/main.py` - Ensure `team_id` is available in handlers

---

## Phase 4: Token Refresh Logic

### 4.1 Automatic Token Refresh

**File:** `app/integrations/zoho_crm.py`

**Logic:**
```python
def refresh_access_token(self):
    # Check if token is expired or about to expire
    # Call Zoho refresh endpoint
    # Update access_token in zoho_installations table
    # Encrypt before storing
```

### 4.2 Handle Refresh Failures

**Scenarios:**
- Refresh token revoked → Mark installation as disconnected
- Zoho account deleted → Clean up installation
- Network errors → Retry with backoff

---

## Phase 5: Environment & Config Changes

### 5.1 New Environment Variables

```bash
# Zoho OAuth (App-level, same for all orgs)
ZOHO_CLIENT_ID=your-zoho-client-id
ZOHO_CLIENT_SECRET=your-zoho-client-secret

# Optional: Default Zoho data center
ZOHO_ACCOUNTS_URL=https://accounts.zoho.com
```

### 5.2 Remove Single-Tenant Variables

**Remove from `.env`:**
```bash
# REMOVE THESE (now stored per-org in DB)
ZOHO_REFRESH_TOKEN=xxx
ZOHO_ACCESS_TOKEN=xxx
```

### 5.3 Update Config Validation

**File:** `app/config/config.py`

- Add `ZOHO_CLIENT_ID`, `ZOHO_CLIENT_SECRET` validation
- Remove single-tenant Zoho token validation

---

## Phase 6: User Experience

### 6.1 Connection Flow for Users

**Option A: Slack Command**
```
/decision connect-zoho
→ Bot sends ephemeral message with "Connect Zoho CRM" button
→ Button opens OAuth URL in browser
→ User approves in Zoho
→ Redirect back with success message
```

**Option B: Web Dashboard**
- Create a simple web page showing connection status
- Button to connect/disconnect Zoho
- URL: `/dashboard?team_id=T123`

### 6.2 Success/Error Pages

**Files:** `app/templates.py`

**Add:**
- `ZOHO_SUCCESS_PAGE_HTML` - Shown after successful Zoho connection
- `ZOHO_ERROR_PAGE_HTML` - Shown if connection fails

---

## Phase 7: Zoho Marketplace Submission

### 7.1 Developer Registration

1. Go to https://developer.zoho.com
2. Sign up / Log in
3. Create new extension project

### 7.2 Extension Manifest

**File:** `plugin-manifest.json`

```json
{
  "name": "Decision Agent",
  "description": "Sync Slack decisions to Zoho CRM",
  "version": "1.0.0",
  "type": "extension",
  "oauth": {
    "client_id": "{{CLIENT_ID}}",
    "redirect_uri": "{{REDIRECT_URI}}",
    "scope": ["ZohoCRM.modules.ALL", "ZohoCRM.settings.ALL"]
  }
}
```

### 7.3 Required Assets

| Asset | Specification |
|-------|---------------|
| App Icon | 128x128 PNG |
| Screenshots | 1280x800, min 3 |
| Demo Video | Optional but recommended |
| Privacy Policy | URL |
| Support URL | URL |
| Documentation | Help guide for users |

### 7.4 Submission Checklist

- [ ] Extension manifest complete
- [ ] OAuth flow working
- [ ] Error handling tested
- [ ] Privacy policy URL
- [ ] Support URL
- [ ] App description
- [ ] Screenshots
- [ ] Testing in sandbox Zoho account

### 7.5 Review Process

- Zoho reviews submissions manually
- Typically 1-2 weeks
- May request changes/fixes
- Once approved, visible in Zoho Marketplace

---

## Phase 8: Testing Plan

### 8.1 Unit Tests

- Test Zoho OAuth flow
- Test token encryption/decryption
- Test sync with mocked Zoho API

### 8.2 Integration Tests

- Test full flow: Slack install → Zoho connect → Create decision → Verify in Zoho
- Test with multiple teams (data isolation)
- Test token refresh

### 8.3 Manual Testing

- Create two test organizations
- Install Slack app in both
- Connect Zoho in both
- Create decisions in each
- Verify no cross-contamination

---

## Implementation Order

| Step | Task | Estimated Time |
|------|------|----------------|
| 1 | Database schema + migration | 1-2 hours |
| 2 | Zoho OAuth endpoints | 2-3 hours |
| 3 | Update ZohoCRMClient for multi-tenant | 2-3 hours |
| 4 | Update sync logic with team_id | 1-2 hours |
| 5 | Token refresh logic | 1-2 hours |
| 6 | Success/error pages | 1 hour |
| 7 | Slack command for connecting | 1-2 hours |
| 8 | Testing | 2-3 hours |
| 9 | Marketplace submission prep | 2-3 hours |

**Total Estimated Time: 2-3 days**

---

## Files to Create/Modify

### New Files
- `alembic/versions/002_add_zoho_installations.py`
- `app/integrations/zoho_oauth.py` (optional, can be in main.py)

### Modified Files
- `app/models.py` - Add ZohoInstallation model
- `app/config/config.py` - Add Zoho OAuth config
- `app/integrations/zoho_crm.py` - Multi-tenant client
- `app/integrations/zoho_sync.py` - Pass team_id
- `app/handlers/decision_handlers.py` - Pass team_id to sync
- `app/main.py` - Add Zoho OAuth endpoints
- `app/templates.py` - Add Zoho success/error pages
- `.env.example` - Add Zoho OAuth variables

---

## Security Considerations

1. **Token Encryption**: Reuse existing Fernet encryption for Zoho tokens
2. **State Parameter**: Prevent CSRF in OAuth flow
3. **Token Storage**: Never log tokens, encrypt at rest
4. **Scope Limitation**: Request only necessary Zoho scopes
5. **Data Isolation**: Always filter by team_id in queries

---

## Rollback Plan

If issues arise:
1. Disable Zoho sync temporarily (feature flag)
2. Keep single-tenant mode as fallback
3. Migration has downgrade function

---

## Success Criteria

- [ ] Multiple orgs can connect their own Zoho CRM
- [ ] Decisions sync to the correct Zoho CRM
- [ ] No data leakage between organizations
- [ ] Token refresh works automatically
- [ ] Published on Zoho Marketplace
