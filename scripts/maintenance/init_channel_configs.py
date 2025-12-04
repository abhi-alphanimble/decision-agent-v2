"""
Initialize ChannelConfig rows for channels in the workspace.

This script will:
- List channels visible to the bot (public and private where the bot is a member)
- For each channel, compute the human member count via `slack_client.get_channel_members_count`
- Create or update a ChannelConfig with `group_size` and optional `auto_close_hours`

Run:
  python scripts/init_channel_configs.py

Optional environment variables:
- DEFAULT_AUTO_CLOSE_HOURS: integer override for auto_close_hours (defaults to 48)
"""

import os
import sys
import logging

# Ensure repository root is on sys.path so `app` imports work when running
# this script from inside `scripts/maintenance/` or from the repo root.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.slack_client import slack_client
from app import crud
from database.base import engine
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def list_all_channels(client):
    """Return list of channel dicts (public + private) available to the bot."""
    channels = []
    next_cursor = None

    while True:
        try:
            resp = client.client.conversations_list(limit=200, cursor=next_cursor, types="public_channel,private_channel")
        except Exception as e:
            logger.error(f"Failed to list channels: {e}")
            break

        channels.extend(resp.get('channels', []))
        next_cursor = resp.get('response_metadata', {}).get('next_cursor')
        if not next_cursor:
            break

    return channels


def main():
    default_hours = int(os.getenv('DEFAULT_AUTO_CLOSE_HOURS', '48'))

    logger.info("Listing channels via Slack API...")
    channels = list_all_channels(slack_client)
    logger.info(f"Found {len(channels)} channels to examine")

    db = Session(engine)
    created = 0
    updated = 0
    skipped = 0

    try:
        for ch in channels:
            channel_id = ch.get('id')
            name = ch.get('name') or ch.get('name_normalized') or channel_id

            try:
                human_count = slack_client.get_channel_members_count(channel_id)
            except Exception as e:
                logger.warning(f"Skipping {channel_id} ({name}): failed to get member count: {e}")
                skipped += 1
                continue

            # Ensure a ChannelConfig exists and is updated
            cfg = crud.get_channel_config(db=db, channel_id=channel_id, default_group_size=human_count)

            # If config was newly created (group_size equals provided human_count and updated_by may be null),
            # consider it created. crud.get_channel_config always creates if missing.
            # We'll call update_channel_config to ensure auto_close_hours is set to desired default if different.
            if cfg.auto_close_hours != default_hours:
                updated_cfg = crud.update_channel_config(
                    db=db,
                    channel_id=channel_id,
                    updated_by='system',
                    updated_by_name='system-init',
                    default_group_size=human_count,
                    auto_close_hours=default_hours,
                    group_size=human_count
                )
                if updated_cfg:
                    logger.info(f"Updated config for {name} ({channel_id}): auto_close_hours {cfg.auto_close_hours} -> {default_hours}, group_size {cfg.group_size} -> {human_count}")
                    updated += 1
                else:
                    logger.warning(f"Failed to update config for {name} ({channel_id})")
                    skipped += 1
            else:
                # Ensure group_size is up-to-date
                if cfg.group_size != human_count:
                    updated_cfg = crud.update_channel_config(
                        db=db,
                        channel_id=channel_id,
                        updated_by='system',
                        updated_by_name='system-init',
                        default_group_size=human_count,
                        group_size=human_count
                    )
                    if updated_cfg:
                        logger.info(f"Updated group_size for {name} ({channel_id}): {cfg.group_size} -> {human_count}")
                        updated += 1
                    else:
                        skipped += 1
                else:
                    logger.info(f"No change for {name} ({channel_id}) — auto_close_hours={cfg.auto_close_hours}, group_size={cfg.group_size}")

        logger.info(f"Done. Updated={updated}, Skipped={skipped}")

    finally:
        db.close()


if __name__ == '__main__':
    main()
