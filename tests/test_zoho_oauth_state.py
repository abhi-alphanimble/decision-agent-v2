"""
Test script for Zoho OAuth state cache verification.

This script tests the cache-based CSRF protection mechanism.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.integrations.zoho_oauth import (
    generate_state,
    verify_and_consume_state,
    get_cache_stats,
    _state_cache
)


def test_basic_flow():
    """Test basic OAuth flow: generate → verify → consume"""
    print("\n🧪 Test 1: Basic OAuth Flow")
    print("=" * 60)
    
    team_id = "T123456789"
    
    # Generate state
    state = generate_state(team_id)
    print(f"✅ Generated state: {state[:30]}...")
    
    # Check cache
    stats = get_cache_stats()
    print(f"📊 Cache stats: {stats}")
    assert stats["total_entries"] == 1, "Should have 1 entry"
    assert stats["active_entries"] == 1, "Should have 1 active entry"
    
    # Verify state
    verified_team_id = verify_and_consume_state(state)
    print(f"✅ Verified team_id: {verified_team_id}")
    assert verified_team_id == team_id, "Team ID should match"
    
    # Check cache after consumption
    stats = get_cache_stats()
    print(f"📊 Cache after consume: {stats}")
    assert stats["total_entries"] == 0, "Should have 0 entries after consumption"
    
    print("✅ Test 1 PASSED\n")


def test_replay_attack_prevention():
    """Test that reusing the same state fails (replay attack prevention)"""
    print("\n🧪 Test 2: Replay Attack Prevention")
    print("=" * 60)
    
    team_id = "T987654321"
    
    # Generate state
    state = generate_state(team_id)
    print(f"✅ Generated state: {state[:30]}...")
    
    # First verification should succeed
    verified_team_id = verify_and_consume_state(state)
    print(f"✅ First verification: {verified_team_id}")
    assert verified_team_id == team_id
    
    # Second verification should fail (nonce consumed)
    verified_team_id = verify_and_consume_state(state)
    print(f"❌ Second verification (should fail): {verified_team_id}")
    assert verified_team_id is None, "Replay should be prevented"
    
    print("✅ Test 2 PASSED\n")


def test_tampering_detection():
    """Test that tampering with state is detected"""
    print("\n🧪 Test 3: Tampering Detection")
    print("=" * 60)
    
    team_id = "T111111111"
    
    # Generate state
    state = generate_state(team_id)
    print(f"✅ Generated state: {state[:30]}...")
    
    # Try to tamper with state (modify team_id in the state)
    import base64
    tampered_state = base64.urlsafe_b64encode(b"T999999999:fake_nonce").decode()
    print(f"🔨 Tampered state: {tampered_state[:30]}...")
    
    # Verification should fail
    verified_team_id = verify_and_consume_state(tampered_state)
    print(f"❌ Tampered verification (should fail): {verified_team_id}")
    assert verified_team_id is None, "Tampering should be detected"
    
    # Original state should still work
    verified_team_id = verify_and_consume_state(state)
    print(f"✅ Original state still works: {verified_team_id}")
    assert verified_team_id == team_id
    
    print("✅ Test 3 PASSED\n")


def test_expiration():
    """Test that expired states are rejected"""
    print("\n🧪 Test 4: Expiration (Simulated)")
    print("=" * 60)
    
    team_id = "T222222222"
    
    # Generate state
    state = generate_state(team_id)
    print(f"✅ Generated state: {state[:30]}...")
    
    # Manually expire the state by modifying the cache
    import base64
    from datetime import datetime, UTC, timedelta
    
    state_data = base64.urlsafe_b64decode(state.encode()).decode()
    _, nonce = state_data.split(":", 1)
    
    # Set expiration to past
    _state_cache[nonce]["expires_at"] = datetime.now(UTC) - timedelta(minutes=1)
    print(f"⏰ Manually expired the state")
    
    # Verification should fail
    verified_team_id = verify_and_consume_state(state)
    print(f"❌ Expired verification (should fail): {verified_team_id}")
    assert verified_team_id is None, "Expired state should be rejected"
    
    print("✅ Test 4 PASSED\n")


def test_multiple_concurrent_flows():
    """Test multiple concurrent OAuth flows"""
    print("\n🧪 Test 5: Multiple Concurrent Flows")
    print("=" * 60)
    
    teams = ["T333", "T444", "T555"]
    states = {}
    
    # Generate states for multiple teams
    for team_id in teams:
        states[team_id] = generate_state(team_id)
        print(f"✅ Generated state for {team_id}")
    
    # Check cache
    stats = get_cache_stats()
    print(f"📊 Cache stats: {stats}")
    assert stats["total_entries"] == 3, "Should have 3 entries"
    
    # Verify each state in random order
    for team_id in reversed(teams):
        verified = verify_and_consume_state(states[team_id])
        print(f"✅ Verified {team_id}: {verified}")
        assert verified == team_id
    
    # Cache should be empty
    stats = get_cache_stats()
    print(f"📊 Final cache stats: {stats}")
    assert stats["total_entries"] == 0, "All states should be consumed"
    
    print("✅ Test 5 PASSED\n")


def test_cache_stats():
    """Test cache statistics function"""
    print("\n🧪 Test 6: Cache Statistics")
    print("=" * 60)
    
    # Generate some states
    for i in range(5):
        generate_state(f"T{i:03d}")
    
    stats = get_cache_stats()
    print(f"📊 Cache stats:")
    print(f"   Total entries: {stats['total_entries']}")
    print(f"   Active entries: {stats['active_entries']}")
    print(f"   Expired entries: {stats['expired_entries']}")
    print(f"   Oldest entry: {stats['oldest_entry']}")
    
    assert stats["total_entries"] == 5, "Should have 5 entries"
    assert stats["active_entries"] == 5, "All should be active"
    assert stats["oldest_entry"] is not None, "Should have oldest entry timestamp"
    
    # Clean up
    _state_cache.clear()
    
    print("✅ Test 6 PASSED\n")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🔐 ZOHO OAUTH STATE CACHE VERIFICATION TESTS")
    print("=" * 60)
    
    try:
        test_basic_flow()
        test_replay_attack_prevention()
        test_tampering_detection()
        test_expiration()
        test_multiple_concurrent_flows()
        test_cache_stats()
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\n✅ Cache-based state verification is working correctly")
        print("✅ CSRF protection is active")
        print("✅ Replay attacks are prevented")
        print("✅ Tampering is detected")
        print("✅ Expiration is enforced")
        print("\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
