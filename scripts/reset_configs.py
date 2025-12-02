#!/usr/bin/env python
"""Delete all channel configs to force re-fetch from Slack"""
from app.models import ChannelConfig
from database.base import engine
from sqlalchemy.orm import Session

db = Session(engine)
configs = db.query(ChannelConfig).all()

print(f"Deleting {len(configs)} channel configs...")
for config in configs:
    channel_id = config.channel_id
    old_size = config.group_size
    db.delete(config)
    db.commit()
    print(f"  ✅ Deleted config for channel {channel_id} (was group_size={old_size})")

print("\n✅ All configs deleted. On next proposal, they will be recreated with actual member count from Slack.")
