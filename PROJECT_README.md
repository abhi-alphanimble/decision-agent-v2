# Slack Decision Agent v2

A **Slack-integrated decision management system** that enables teams to make democratic decisions through a structured voting process. The agent provides a `/decision` slash command that allows team members to propose, vote on, and track decisions with support for anonymous voting, AI-powered summaries, and configurable approval thresholds.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup Guide](#-setup-guide)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [Database Migrations](#-database-migrations)
- [Testing](#-testing)
- [Scripts Reference](#-scripts-reference)
- [API Endpoints](#-api-endpoints)

---

## 🎯 Overview

The Slack Decision Agent is a FastAPI-powered backend service that integrates with Slack to facilitate team decision-making. When installed in a Slack workspace, it provides:

1. **Decision Proposals** - Create decisions for team voting
2. **Democratic Voting** - Approve or reject decisions with support for anonymous votes
3. **Configurable Thresholds** - Set approval percentages, auto-close timeouts, and group sizes per channel
4. **AI Insights** - Get AI-powered summaries and suggestions using Google Gemini
5. **Multi-Workspace Support** - OAuth 2.0 based installation for multiple workspaces

---

## ✨ Features

### Core Features
| Feature | Description |
|---------|-------------|
| **Propose Decisions** | Create new decisions with quoted text for team voting |
| **Voting System** | Approve or reject decisions with real-time vote counting |
| **Anonymous Voting** | Cast votes anonymously (hidden from others, visible to you) |
| **Vote Tracking** | Track who voted and how (respecting anonymity settings) |
| **Decision Status** | Automatic status changes: pending → approved/rejected/expired |
| **Per-Channel Config** | Configure approval thresholds, timeout hours, and group sizes |

### AI Features (Optional)
| Feature | Description |
|---------|-------------|
| **AI Summaries** | Get AI-generated summaries of decisions and voting status |
| **AI Suggestions** | Receive actionable next-step suggestions based on voting progress |

### Administrative
| Feature | Description |
|---------|-------------|
| **Channel Configuration** | Admins can set `approval_percentage`, `auto_close_hours`, `group_size` |
| **Change Logging** | All configuration changes are logged with timestamps and user info |
| **Multi-Workspace OAuth** | Install the app in multiple Slack workspaces |

---

## 🏗 Architecture

```
┌─────────────────┐     ┌─────────────────────────┐     ┌──────────────────┐
│   Slack API     │────▶│   FastAPI Application   │────▶│   PostgreSQL     │
│  (Slash Command │     │   (main.py)             │     │   Database       │
│   & Events)     │     │                         │     │                  │
└─────────────────┘     │  ┌───────────────────┐  │     └──────────────────┘
                        │  │ Command Parser    │  │
                        │  │ (command_parser)  │  │     ┌──────────────────┐
                        │  └───────────────────┘  │────▶│  Google Gemini   │
                        │                         │     │  (AI Summaries)  │
                        │  ┌───────────────────┐  │     └──────────────────┘
                        │  │ Decision Handlers │  │
                        │  │ (handlers/)       │  │
                        │  └───────────────────┘  │
                        │                         │
                        │  ┌───────────────────┐  │
                        │  │ CRUD Operations   │  │
                        │  │ (database/crud)   │  │
                        │  └───────────────────┘  │
                        └─────────────────────────┘
```

### Request Flow

1. **Slack sends a slash command** → `/webhook/slack` endpoint
2. **Command is parsed** → `command_parser.py` extracts action, args, and flags
3. **Handler processes request** → `decision_handlers.py` routes to appropriate handler
4. **Database operations** → `crud.py` performs CRUD operations
5. **Response sent back** → via `response_url` (slash commands) or direct message (events)

---

## 🛠 Tech Stack

| Category | Technology |
|----------|------------|
| **Backend Framework** | FastAPI 0.123+ |
| **Database** | PostgreSQL with SQLAlchemy 2.0+ ORM |
| **Migrations** | Alembic |
| **Slack SDK** | slack-sdk 3.39+ |
| **AI Integration** | Google Generative AI (Gemini 2.5 Flash) |
| **Validation** | Pydantic 2.12+ |
| **Server** | Uvicorn |
| **Package Manager** | uv (modern Python package manager) |
| **Testing** | pytest with pytest-cov |

---

## 📁 Project Structure

```
decision-agent-v2/
├── main.py                    # Main FastAPI application entry point
├── run.py                     # Alternative runner script
├── pyproject.toml             # Project dependencies (uv/pip)
├── requirements.txt           # Legacy requirements file
├── alembic.ini                # Alembic configuration
├── .env.example               # Environment variables template
│
├── app/                       # Main application package
│   ├── __init__.py
│   ├── main.py                # Application factory (alternative)
│   ├── models.py              # SQLAlchemy ORM models
│   ├── schemas.py             # Pydantic schemas
│   ├── command_parser.py      # Slack command parsing logic
│   ├── dependencies.py        # FastAPI dependencies
│   ├── exceptions.py          # Custom exceptions
│   ├── logging_config.py      # Logging configuration
│   │
│   ├── ai/                    # AI integration
│   │   └── ai_client.py       # Google Gemini client
│   │
│   ├── config/                # Configuration
│   │   ├── __init__.py
│   │   ├── config.py          # Environment configuration
│   │   └── logging.py         # Structured logging
│   │
│   ├── database/              # Database layer
│   │   ├── __init__.py
│   │   └── crud.py            # CRUD operations
│   │
│   ├── handlers/              # Command handlers
│   │   ├── commands.py        # Command routing
│   │   ├── decision_handlers.py  # Decision-related handlers
│   │   └── member_handlers.py    # Member-related handlers
│   │
│   ├── slack/                 # Slack integration
│   │   ├── __init__.py
│   │   ├── client.py          # Slack WebClient wrapper
│   │   └── oauth.py           # OAuth 2.0 flow
│   │
│   └── utils/                 # Utility functions
│       └── display.py         # Message formatting utilities
│
├── database/                  # Database configuration
│   ├── __init__.py
│   └── base.py                # SQLAlchemy engine and session
│
├── alembic/                   # Database migrations
│   ├── env.py                 # Alembic environment
│   ├── script.py.mako         # Migration template
│   └── versions/              # Migration files
│       ├── 60751c4d60fc_initial_migration_*.py
│       ├── 88f915c66504_add_channel_config_*.py
│       └── 8b146b2fa096_add_slack_installations_*.py
│
├── scripts/                   # Utility scripts
│   ├── admin/                 # Admin scripts
│   │   ├── get_bot_token.py
│   │   ├── inspect_decisions.py
│   │   └── list_channel_members.py
│   ├── devops/                # DevOps scripts
│   ├── integrations/          # Integration scripts
│   └── maintenance/           # Maintenance scripts
│       ├── check_config.py
│       ├── fix_sequence.py
│       ├── init_channel_configs.py
│       ├── reset_configs.py
│       └── sync_group_sizes.py
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py            # Pytest fixtures
│   ├── test_api.py            # API endpoint tests
│   ├── test_db.py             # Database tests
│   ├── test_handlers.py       # Handler tests
│   └── test_server.py         # Server tests
│
└── stubs/                     # Type stubs for mypy
    ├── alembic.pyi
    ├── httpx.pyi
    ├── pythonjsonlogger.pyi
    ├── slack_sdk.pyi
    ├── httpx/
    ├── slack_sdk/
    └── sqlalchemy/
```

---

## 🚀 Setup Guide

### Prerequisites

- **Python 3.13+** (required)
- **PostgreSQL 13+** (database)
- **Slack App** (with proper permissions)
- **Google Cloud API Key** (optional, for AI features)

### Step 1: Clone and Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd decision-agent-v2

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Or using pip
pip install -r requirements.txt
```

### Step 2: Set Up PostgreSQL Database

```bash
# Create the database
createdb decision_agent

# Or via psql
psql -U postgres -c "CREATE DATABASE decision_agent;"
```

### Step 3: Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values
nano .env
```

**Required Environment Variables:**

```env
# Database Configuration
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=decision_agent

# Slack Configuration (from Slack App settings)
SLACK_CLIENT_ID=your_client_id
SLACK_CLIENT_SECRET=your_client_secret
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your_signing_secret
SLACK_APP_ID=your_app_id

# AI Configuration (optional)
GEMINI_API_KEY=your_gemini_api_key

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

### Step 4: Run Database Migrations

```bash
# Run all pending migrations
alembic upgrade head
```

### Step 5: Start the Server

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 6: Set Up Slack App

1. Go to [https://api.slack.com/apps](https://api.slack.com/apps)
2. Click "Create New App" → "From scratch"
3. Configure the following:

**OAuth & Permissions → Scopes:**
- `chat:write`
- `commands`
- `app_mentions:read`
- `channels:history`
- `groups:history`
- `im:history`
- `mpim:history`

**Slash Commands:**
- Command: `/decision`
- Request URL: `https://your-domain.com/webhook/slack`
- Description: "Create and vote on team decisions"

**Event Subscriptions:**
- Request URL: `https://your-domain.com/slack/events`
- Subscribe to: `app_mention`, `message.channels`

**OAuth Redirect URL:**
- `https://your-domain.com/slack/install/callback`

4. Install the app to your workspace
5. Copy the Bot Token and add it to your `.env` file

---

## ⚙️ Configuration

### Channel-Level Configuration

Each Slack channel can have its own configuration:

| Setting | Default | Description |
|---------|---------|-------------|
| `approval_percentage` | 60 | Percentage of votes needed to approve (1-100) |
| `auto_close_hours` | 48 | Hours before a decision auto-expires |
| `group_size` | 10 | Number of members for threshold calculation |

**Configure via Slack:**
```
/decision config show
/decision config set approval_percentage 70
/decision config set auto_close_hours 72
/decision config set group_size 15
```

---

## 📖 Usage Guide

### Creating Proposals

```
/decision propose "Should we switch to Python 3.13?"
/decision add "Deploy new feature to production" (pre-approved)
```

### Voting

```
/decision approve 42
/decision reject 42
/decision approve 42 --anonymous   # Vote anonymously
/decision approve 42 -a            # Short form
```

### Viewing Decisions

```
/decision list                     # All decisions in channel
/decision list pending             # Only pending decisions
/decision list approved            # Only approved decisions
/decision show 42                  # Full details of decision #42
/decision myvote 42                # Check your vote on decision #42
/decision search "keyword"         # Search decisions
```

### AI Features (if configured)

```
/decision summarize 42             # AI summary of decision
/decision suggest 42               # AI suggestions for next steps
```

### Help

```
/decision help
```

---

## 🔄 Database Migrations

### Common Commands

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to a specific revision
alembic downgrade <revision_id>

# Show current revision
alembic current

# Show migration history
alembic history
```

### Database Models

| Model | Description |
|-------|-------------|
| `Decision` | Stores proposal text, status, vote counts, thresholds |
| `Vote` | Individual votes with anonymous flag |
| `SlackInstallation` | OAuth tokens for multi-workspace support |
| `ChannelConfig` | Per-channel configuration settings |
| `ConfigChangeLog` | Audit log for configuration changes |

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_handlers.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_handlers.py::test_propose_command
```

### Test Configuration

Tests use:
- **SQLite in-memory** by default (for fast local testing)
- **PostgreSQL** if `TEST_DATABASE_URL` is set (for CI/production-like tests)
- **Mock Slack/AI clients** to avoid external API calls

---

## 📜 Scripts Reference

### Admin Scripts (`scripts/admin/`)

| Script | Description |
|--------|-------------|
| `get_bot_token.py` | Retrieve bot token from database |
| `inspect_decisions.py` | Inspect decision data in database |
| `list_channel_members.py` | List members of a Slack channel |

### Maintenance Scripts (`scripts/maintenance/`)

| Script | Description |
|--------|-------------|
| `check_config.py` | Check channel configurations |
| `fix_sequence.py` | Fix PostgreSQL sequence issues |
| `init_channel_configs.py` | Initialize default channel configs |
| `reset_configs.py` | Reset configurations to defaults |
| `sync_group_sizes.py` | Sync group sizes with Slack |

---

## 🌐 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check (simple) |
| `/health` | GET | Detailed health check |
| `/webhook/slack` | POST | Slack slash command handler |
| `/slack/events` | POST | Slack events webhook |
| `/slack/install` | GET | OAuth install flow start |
| `/slack/install/callback` | GET | OAuth callback handler |

---

## 🔧 Development

### Code Style

- Follow PEP 8 guidelines
- Use type hints throughout
- Document public functions with docstrings

### Logging

Structured JSON logging is configured for production. In development, logs are human-readable.

### Adding New Commands

1. Add the action to `DecisionAction` enum in `command_parser.py`
2. Add parsing logic in `parse_message()` function
3. Create handler function in `decision_handlers.py`
4. Route the command in `main.py`'s `process_command_async()`

---

## 📄 License

[Add your license information here]

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Submit a pull request

---

## 📞 Support

For issues and feature requests, please use the GitHub issue tracker.
