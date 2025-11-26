"""
Test script for auto-close functionality

This script allows you to manually test the auto-close job without waiting for the scheduler.
It also helps create test data with backdated timestamps.
"""
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.base import SessionLocal
from app.models import Decision
from app.jobs.auto_close import check_stale_decisions


def create_test_decision(hours_old: int, approvals: int, rejections: int, channel_id: str = "C12345"):
    """
    Create a test decision with backdated timestamp.
    
    Args:
        hours_old: How many hours ago the decision was created
        approvals: Number of approvals
        rejections: Number of rejections
        channel_id: Slack channel ID
    """
    db = SessionLocal()
    
    try:
        # Create decision with backdated timestamp
        decision = Decision(
            text=f"Test decision created {hours_old}h ago (👍{approvals} 👎{rejections})",
            proposer_id="U12345",
            proposer_name="Test User",
            channel_id=channel_id,
            status="pending",
            approval_count=approvals,
            rejection_count=rejections,
            created_at=datetime.utcnow() - timedelta(hours=hours_old)
        )
        
        db.add(decision)
        db.commit()
        db.refresh(decision)
        
        print(f"✅ Created test decision #{decision.id}: {decision.text}")
        return decision.id
        
    except Exception as e:
        print(f"❌ Error creating test decision: {e}")
        db.rollback()
        return None
        
    finally:
        db.close()


def run_manual_test():
    """Run the auto-close job manually for testing."""
    print("\n🧪 Running manual auto-close test...\n")
    
    # Create test decisions
    print("📝 Creating test decisions...")
    create_test_decision(hours_old=50, approvals=5, rejections=2, channel_id="C12345")  # Should approve
    create_test_decision(hours_old=49, approvals=1, rejections=4, channel_id="C12345")  # Should reject
    create_test_decision(hours_old=48, approvals=3, rejections=3, channel_id="C12345")  # Should expire (tie)
    create_test_decision(hours_old=24, approvals=2, rejections=1, channel_id="C12345")  # Should NOT close (too new)
    
    print("\n⏳ Running auto-close job...\n")
    
    # Run the job
    check_stale_decisions()
    
    print("\n✅ Test complete! Check the logs above for results.")
    print("💡 Tip: Check your Slack channel for notifications (if configured correctly)")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test auto-close functionality")
    parser.add_argument("--create", action="store_true", help="Create test decisions only")
    parser.add_argument("--run", action="store_true", help="Run auto-close job only")
    parser.add_argument("--hours", type=int, default=50, help="Hours old for test decision")
    parser.add_argument("--approvals", type=int, default=5, help="Number of approvals")
    parser.add_argument("--rejections", type=int, default=2, help="Number of rejections")
    
    args = parser.parse_args()
    
    if args.create:
        create_test_decision(args.hours, args.approvals, args.rejections)
    elif args.run:
        check_stale_decisions()
    else:
        run_manual_test()
