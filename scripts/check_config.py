#!/usr/bin/env python
"""Check database configs"""
from app.models import ChannelConfig
from database.base import engine
from sqlalchemy.orm import Session

db = Session(engine)
configs = db.query(ChannelConfig).all()

print(f"Total configs: {len(configs)}")
for config in configs:
    print(f"  Channel {config.channel_id}: group_size={config.group_size}, approval_percentage={config.approval_percentage}")
