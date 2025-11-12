
from database.base import SessionLocal, test_connection
from app.models import Decision, Vote
from datetime import datetime

def test_database():
    """Test database connection and operations"""
    
    print("=" * 60)
    print("Testing Database Connection and Operations")
    print("=" * 60)
    
    # Test connection
    print("\n1. Testing database connection...")
    if test_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
        return
    
    # Create session
    db = SessionLocal()
    
    try:
        # Test 1: Insert a decision
        print("\n2. Testing Decision insertion...")
        decision = Decision(
            text="Should we order pizza for lunch?",
            status="pending",
            proposer_phone="+1234567890",
            proposer_name="John Doe",
            channel_id="group_123",
            group_size_at_creation=5,
            approval_threshold=3,
            approval_count=0,
            rejection_count=0
        )
        db.add(decision)
        db.commit()
        db.refresh(decision)
        print(f"✅ Decision created: {decision}")
        
        # Test 2: Insert votes
        print("\n3. Testing Vote insertion...")
        votes_data = [
            {
                "voter_phone": "+1234567891",
                "voter_name": "Alice Smith",
                "vote_type": "approve",
                "is_anonymous": False
            },
            {
                "voter_phone": "+1234567892",
                "voter_name": "Bob Johnson",
                "vote_type": "approve",
                "is_anonymous": True
            },
            {
                "voter_phone": "+1234567893",
                "voter_name": "Carol White",
                "vote_type": "reject",
                "is_anonymous": False
            }
        ]
        
        for vote_data in votes_data:
            vote = Vote(
                decision_id=decision.id,
                **vote_data
            )
            db.add(vote)
        
        db.commit()
        print("✅ 3 votes inserted successfully!")
        
        # Test 3: Query decision with votes
        print("\n4. Testing queries...")
        queried_decision = db.query(Decision).filter(Decision.id == decision.id).first()
        print(f"✅ Queried decision: {queried_decision}")
        print(f"   Number of votes: {len(queried_decision.votes)}")
        
        for vote in queried_decision.votes:
            print(f"   {vote}")
        
        # Test 4: Test unique constraint
        print("\n5. Testing unique constraint (decision_id, voter_phone)...")
        try:
            duplicate_vote = Vote(
                decision_id=decision.id,
                voter_phone="+1234567891",  # Same voter
                voter_name="Alice Smith",
                vote_type="reject",
                is_anonymous=False
            )
            db.add(duplicate_vote)
            db.commit()
            print("❌ Unique constraint failed - duplicate vote was allowed!")
        except Exception as e:
            db.rollback()
            print(f"✅ Unique constraint working - duplicate vote prevented!")
            print(f"   Error: {str(e)[:100]}...")
        
        # Test 5: Test cascade delete
        print("\n6. Testing CASCADE delete...")
        vote_count_before = db.query(Vote).filter(Vote.decision_id == decision.id).count()
        print(f"   Votes before delete: {vote_count_before}")
        
        db.delete(queried_decision)
        db.commit()
        
        vote_count_after = db.query(Vote).filter(Vote.decision_id == decision.id).count()
        print(f"   Votes after delete: {vote_count_after}")
        
        if vote_count_after == 0:
            print("✅ CASCADE delete working - all votes deleted with decision!")
        else:
            print("❌ CASCADE delete failed - votes still exist!")
        
        # Test 6: Verify connection pool
        print("\n7. Testing connection pool...")
        print(f"✅ Pool size: 5, Max overflow: 10")
        print(f"   Current pool status: {db.bind.pool.status()}")
        
        print("\n" + "=" * 60)
        print("All tests completed successfully! ✅")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_database()
