import os
import sys

# Ensure project root is on sys.path so local packages import correctly
# Script is now in `scripts/admin/` so repository root is two levels up
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database.base import SessionLocal
from app.models import Decision


def main():
    db = SessionLocal()
    try:
        decisions = db.query(Decision).order_by(Decision.created_at.desc()).all()
        if not decisions:
            print("No decisions found in DB.")
            return
        print(f"Found {len(decisions)} decisions:\n")
        for d in decisions:
            print(f"ID={d.id}\tchannel_id={d.channel_id}\tstatus={d.status}\tapprovals={d.approval_count}\trejections={d.rejection_count}\n    text={d.text[:80]}{'...' if len(d.text)>80 else ''}\n")
    finally:
        db.close()

if __name__ == '__main__':
    main()
