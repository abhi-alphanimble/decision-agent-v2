#!/usr/bin/env python
"""Check database configs"""
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

print(f"Total configs: {len(configs)}")
for config in configs:
    print(f"  Channel {config.channel_id}: group_size={config.group_size}, approval_percentage={config.approval_percentage}")
