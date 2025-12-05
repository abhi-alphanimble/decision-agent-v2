"""
Fix PostgreSQL sequence for decisions table.

This script resets the decision ID sequence to continue from the maximum
existing ID, fixing gaps caused by rolled-back transactions.

Run this when decision IDs are jumping unexpectedly.
"""
import os
import sys

# Ensure repository root is on sys.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from sqlalchemy import text
from database.base import SessionLocal, engine

def fix_decision_sequence():
    """Reset the decisions_id_seq to continue from max(id) + 1"""
    db = SessionLocal()
    
    try:
        # Get the current max ID
        result = db.execute(text("SELECT COALESCE(MAX(id), 0) FROM decisions"))
        max_id = result.scalar()
        
        print(f"Current max decision ID: {max_id}")
        
        # Get current sequence value
        result = db.execute(text("SELECT last_value FROM decisions_id_seq"))
        current_seq = result.scalar()
        print(f"Current sequence value: {current_seq}")
        
        if current_seq > max_id + 1:
            # Reset sequence to max_id + 1
            new_seq = max_id + 1
            db.execute(text(f"SELECT setval('decisions_id_seq', {new_seq}, false)"))
            db.commit()
            print(f"✅ Sequence reset to {new_seq}")
        else:
            print(f"✅ Sequence is already correct (next ID will be {current_seq})")
        
        # Verify
        result = db.execute(text("SELECT last_value FROM decisions_id_seq"))
        final_seq = result.scalar()
        print(f"Final sequence value: {final_seq}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


def fix_vote_sequence():
    """Reset the votes_id_seq to continue from max(id) + 1"""
    db = SessionLocal()
    
    try:
        # Get the current max ID
        result = db.execute(text("SELECT COALESCE(MAX(id), 0) FROM votes"))
        max_id = result.scalar()
        
        print(f"\nCurrent max vote ID: {max_id}")
        
        # Get current sequence value
        result = db.execute(text("SELECT last_value FROM votes_id_seq"))
        current_seq = result.scalar()
        print(f"Current sequence value: {current_seq}")
        
        if current_seq > max_id + 1:
            # Reset sequence to max_id + 1
            new_seq = max_id + 1
            db.execute(text(f"SELECT setval('votes_id_seq', {new_seq}, false)"))
            db.commit()
            print(f"✅ Sequence reset to {new_seq}")
        else:
            print(f"✅ Sequence is already correct (next ID will be {current_seq})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("PostgreSQL Sequence Fixer")
    print("=" * 50)
    
    fix_decision_sequence()
    fix_vote_sequence()
    
    print("\n✅ Done!")
