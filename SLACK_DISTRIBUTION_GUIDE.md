# Slack App Configuration Guide

Complete checklist for configuring your Slack app for multi-workspace distribution.

---

## 1. Environment Setup

### Generate Encryption Key
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Update `.env` File
```bash
# Slack OAuth Credentials (get from api.slack.com → Your App → Basic Information)
SLACK_CLIENT_ID=your-client-id
SLACK_CLIENT_SECRET=your-client-secret
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_ID=your-app-id

# Token Encryption
TOKEN_ENCRYPTION_KEY=your-generated-key-from-above

# App URL (your ngrok domain)
APP_BASE_URL=https://danette-cerebroid-uneuphemistically.ngrok-free.dev

# Database
DB_PASSWORD=your-db-password
```

### Run Database Migrations
```bash
uv run alembic upgrade head
```

---

## 2. Slack App Dashboard Configuration

Go to **https://api.slack.com/apps**

### Step 1: Create App
1. Click **"Create New App"** → **"From scratch"**
2. **App Name:** Decision Agent
3. **Development Workspace:** Select your workspace
4. Click **"Create App"**

---

### Step 2: Basic Information

**Display Information:**
- **Short Description:** Group decision-making bot with voting
- **Long Description:** (Write 2-3 sentences about the app)
- **Background Color:** `#667eea`
- **App Icon:** Upload 512x512 PNG

**App Credentials** (copy to your `.env`):
- Copy **App ID** → `SLACK_APP_ID`
- Copy **Client ID** → `SLACK_CLIENT_ID`
- Copy **Client Secret** → `SLACK_CLIENT_SECRET`
- Copy **Signing Secret** → `SLACK_SIGNING_SECRET`

---

### Step 3: OAuth & Permissions

**Redirect URLs:**
1. Click **"Add New Redirect URL"**
2. Enter: `https://danette-cerebroid-uneuphemistically.ngrok-free.dev/slack/install/callback`
3. Click **"Add"** then **"Save URLs"**

**Bot Token Scopes** (add all 13):
- `chat:write`
- `chat:write.public`
- `commands`
- `app_mentions:read`
- `channels:history`
- `groups:history`
- `im:history`
- `mpim:history`
- `users:read`
- `channels:read`
- `groups:read`
- `team:read`
- `channels:join`

---

### Step 4: Slash Commands

1. Click **"Create New Command"**
2. Fill in:
   - **Command:** `/decision`
   - **Request URL:** `https://danette-cerebroid-uneuphemistically.ngrok-free.dev/webhook/slack`
   - **Short Description:** Create and vote on group decisions
   - **Usage Hint:** `propose "text" | approve <id> | reject <id> | list`
3. Click **"Save"**

---

### Step 5: Event Subscriptions

1. Toggle **"Enable Events"** to **ON**
2. **Request URL:** `https://danette-cerebroid-uneuphemistically.ngrok-free.dev/slack/events`
   - ⚠️ Your server must be running to verify
3. Wait for ✅ **Verified**
4. **Subscribe to bot events** (add all):
   - `app_uninstalled`
   - `tokens_revoked`
   - `member_joined_channel`
   - `member_left_channel`
   - `app_mention` (optional)
5. Click **"Save Changes"**

---

### Step 6: Interactivity & Shortcuts

1. Toggle **"Interactivity"** to **ON**
2. **Request URL:** `https://danette-cerebroid-uneuphemistically.ngrok-free.dev/webhook/slack`
3. Click **"Save Changes"**

---

### Step 7: Manage Distribution

**App Directory Information:**
- **Privacy Policy URL:** `https://danette-cerebroid-uneuphemistically.ngrok-free.dev/privacy`
- **Support URL:** `https://danette-cerebroid-uneuphemistically.ngrok-free.dev/support`

**Activate Distribution:**
- Click **"Activate Public Distribution"** (or leave as private)

---

## 3. Start the Application

```bash
# Terminal 1: Start server
uv run uvicorn main:app --reload

# Terminal 2: Start ngrok
ngrok http 8000 --domain=danette-cerebroid-uneuphemistically.ngrok-free.dev
```

---

## 4. Test Installation

1. Visit: `https://danette-cerebroid-uneuphemistically.ngrok-free.dev/slack/install`
2. Click **"Allow"** on Slack
3. You should see: 🎉 **Installation Successful!**
4. Test in Slack: `/decision help`

---

## 5. Verification Checklist

- [ ] All environment variables set in `.env`
- [ ] Database migrations run
- [ ] OAuth redirect URL configured
- [ ] All 13 bot scopes added
- [ ] Slash command `/decision` created
- [ ] Event subscriptions verified (green checkmark)
- [ ] Interactivity enabled
- [ ] Privacy & support URLs set
- [ ] Server and ngrok running
- [ ] Installation successful
- [ ] Commands working in Slack

---

## Troubleshooting

### "Invalid redirect_uri"
- Check `APP_BASE_URL` in `.env` matches Slack dashboard exactly
- Restart server after changing `.env`

### Event subscriptions not verified
- Ensure uvicorn is running
- Ensure ngrok is running with correct domain
- Check ngrok dashboard for incoming requests

### "Failed to complete app installation"
- Check server logs for errors
- Verify `TOKEN_ENCRYPTION_KEY` is set
- Ensure database is running

---

**Need help?** Check server logs or test `/health` endpoint
