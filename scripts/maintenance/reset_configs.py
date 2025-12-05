#!/usr/bin/env python
"""Delete all channel configs to force re-fetch from Slack"""
import os
import sys

# Ensure repository root is on sys.path so `app` imports work when running
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.models import ChannelConfig
from database.base import SessionLocal

db = SessionLocal()
configs = db.query(ChannelConfig).all()

print(f"Deleting {len(configs)} channel configs...")
for config in configs:
    channel_id = config.channel_id
    old_size = config.group_size
    db.delete(config)
    db.commit()
    print(f"  ✅ Deleted config for channel {channel_id} (was group_size={old_size})")

print("\n✅ All configs deleted. On next proposal, they will be recreated with actual member count from Slack.")
