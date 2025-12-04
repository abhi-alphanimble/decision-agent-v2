"""
Script to retrieve the latest bot token from the database
"""
import sys
import os

# Ensure repository root is on sys.path (script lives in `scripts/admin/`)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database.base import SessionLocal
from app.models import SlackInstallation


def get_latest_token():
    """Get the most recently installed workspace token."""
    db = SessionLocal()
    
    try:
        # Get the most recent installation
        installation = db.query(SlackInstallation).order_by(
            SlackInstallation.installed_at.desc()
        ).first()
        
        if installation:
            print(f"\n✅ Found installation for workspace: {installation.team_name}")
            print(f"   Team ID: {installation.team_id}")
            print(f"   Bot User ID: {installation.bot_user_id}")
            print(f"   Installed at: {installation.installed_at}")
            print(f"\n🔑 Bot Token:")
            print(f"   {installation.access_token}")
            print(f"\n💡 Update your .env file with:")
            print(f"   SLACK_BOT_TOKEN={installation.access_token}")
            return installation.access_token
        else:
            print("❌ No installations found in database")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
        
    finally:
        db.close()


if __name__ == "__main__":
    get_latest_token()
