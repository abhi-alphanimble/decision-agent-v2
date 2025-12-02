"""One-off script to sync ChannelConfig.group_size from Slack (filtered human count).

This script will:
- Iterate over existing ChannelConfig rows
- For each channel, call slack_client.get_channel_members_count(channel_id) which
  returns the filtered human count (excludes bots/deleted and the app itself)
- If the fetched count differs from stored `group_size`, call `crud.update_channel_config`
  to update the value (this logs changes to ConfigChangeLog)

Run:
  python sync_group_sizes.py

"""
from app.slack_client import slack_client
from app import crud
from app.models import ChannelConfig
from database.base import engine
from sqlalchemy.orm import Session

EXPLAIN = True


def main():
    db = Session(engine)
    configs = db.query(ChannelConfig).all()
    print(f"Found {len(configs)} channel configs to check.")

    updated = []
    skipped = []

    for cfg in configs:
        channel_id = cfg.channel_id
        try:
            count = slack_client.get_channel_members_count(channel_id)
        except Exception as e:
            print(f"Skipping {channel_id}: failed to fetch members: {e}")
            skipped.append(channel_id)
            continue

        if not isinstance(count, int) or count <= 0:
            print(f"Skipping {channel_id}: invalid count={count}")
            skipped.append(channel_id)
            continue

        if cfg.group_size != count:
            print(f"Updating {channel_id}: {cfg.group_size} -> {count}")
            # Use update_channel_config to log changes
            updated_cfg = crud.update_channel_config(
                db=db,
                channel_id=channel_id,
                updated_by='system',
                updated_by_name='system-sync',
                default_group_size=count,
                group_size=count
            )
            if updated_cfg:
                updated.append((channel_id, cfg.group_size, count))
            else:
                print(f"Failed to update config for {channel_id}")
                skipped.append(channel_id)
        else:
            print(f"No change for {channel_id}: still {cfg.group_size}")

    print("\nSummary:")
    print(f"  Updated: {len(updated)}")
    for ch, old, new in updated:
        print(f"    - {ch}: {old} -> {new}")
    print(f"  Skipped: {len(skipped)}")
    if skipped:
        for ch in skipped:
            print(f"    - {ch}")


if __name__ == '__main__':
    main()
