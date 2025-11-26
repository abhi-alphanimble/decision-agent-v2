"""
Test script to verify environment variables are loading correctly
"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("ENVIRONMENT VARIABLE CHECK")
print("=" * 60)

# Load .env file
load_dotenv()

# Check Slack credentials
slack_vars = {
    'SLACK_CLIENT_ID': os.getenv('SLACK_CLIENT_ID'),
    'SLACK_CLIENT_SECRET': os.getenv('SLACK_CLIENT_SECRET'),
    'SLACK_BOT_TOKEN': os.getenv('SLACK_BOT_TOKEN'),
    'SLACK_SIGNING_SECRET': os.getenv('SLACK_SIGNING_SECRET'),
}

print("\nSlack Configuration:")
print("-" * 60)
for key, value in slack_vars.items():
    if value:
        # Show first 20 chars for security
        display_value = value[:20] + "..." if len(value) > 20 else value
        print(f"✅ {key}: {display_value}")
    else:
        print(f"❌ {key}: NOT SET")

print("\n" + "=" * 60)

# Check if all required vars are set
missing = [k for k, v in slack_vars.items() if not v]
if missing:
    print(f"\n⚠️  WARNING: Missing variables: {', '.join(missing)}")
    print("\nPlease set these in your .env file:")
    for var in missing:
        print(f"   {var}=your_value_here")
else:
    print("\n✅ All Slack credentials are configured!")

print("=" * 60)
