import os
import sys

# Ensure repository root is on sys.path so `app` imports work when running
# this script from inside `scripts/admin/`
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.slack.client import slack_client

CHANNEL_ID = "C09TLG56DU6"  # main channel

print(f"Listing members for channel: {CHANNEL_ID}\n")

client = slack_client._get_client()
try:
    members_response = client.conversations_members(channel=CHANNEL_ID)
    member_ids = members_response.get('members', [])
    print(f"Raw members count from conversations_members: {len(member_ids)}\n")

    human_ids = []
    for uid in member_ids:
        try:
            user_resp = client.users_info(user=uid)
            user = user_resp.get('user', {})
        except Exception as e:
            print(f"- {uid}: ERROR fetching user info: {e}")
            continue

        is_bot = user.get('is_bot', False)
        deleted = user.get('deleted', False)
        name = user.get('name') or user.get('id')
        real_name = user.get('real_name') or ''
        profile = user.get('profile', {})
        display_name = profile.get('display_name') or profile.get('real_name') or ''

        print(f"- {uid}: name={name}, real_name={real_name}, display_name={display_name}, is_bot={is_bot}, deleted={deleted}")

        if not is_bot and not deleted:
            human_ids.append(uid)

    print(f"\nFiltered human count (not bot, not deleted): {len(human_ids)}")
    if human_ids:
        print("Human member IDs:")
        for h in human_ids:
            print(" -", h)

except Exception as e:
    print(f"Failed to list members: {e}")
