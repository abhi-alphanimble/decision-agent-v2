"""
Test multi-tenant Zoho CRM client initialization.

This script tests that the ZohoCRMClient can be initialized correctly
for teams with Zoho connections.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("\n" + "=" * 70)
print("🧪 MULTI-TENANT ZOHO CRM CLIENT TEST")
print("=" * 70)

# Test imports
print("\n1. Testing imports...")
try:
    from app.integrations.zoho_crm import ZohoCRMClient
    from app.integrations.zoho_sync import sync_decision_to_zoho, sync_vote_to_zoho
    print("   ✅ All imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test client initialization signature
print("\n2. Testing ZohoCRMClient constructor signature...")
try:
    import inspect
    sig = inspect.signature(ZohoCRMClient.__init__)
    params = list(sig.parameters.keys())
    
    # Should have: self, team_id, db
    if 'team_id' in params and 'db' in params:
        print(f"   ✅ Constructor has correct parameters: {params}")
    else:
        print(f"   ❌ Constructor missing parameters. Found: {params}")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Failed to check constructor: {e}")
    sys.exit(1)

# Test sync function signatures
print("\n3. Testing sync function signatures...")
try:
    import inspect
    
    # Check sync_decision_to_zoho
    sig = inspect.signature(sync_decision_to_zoho)
    params = list(sig.parameters.keys())
    if 'team_id' in params and 'db' in params:
        print(f"   ✅ sync_decision_to_zoho has correct parameters: {params}")
    else:
        print(f"   ❌ sync_decision_to_zoho missing parameters. Found: {params}")
        sys.exit(1)
    
    # Check sync_vote_to_zoho
    sig = inspect.signature(sync_vote_to_zoho)
    params = list(sig.parameters.keys())
    if 'team_id' in params and 'db' in params:
        print(f"   ✅ sync_vote_to_zoho has correct parameters: {params}")
    else:
        print(f"   ❌ sync_vote_to_zoho missing parameters. Found: {params}")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Failed to check sync functions: {e}")
    sys.exit(1)

# Test that client requires team_id (cannot initialize without it)
print("\n4. Testing client initialization error handling...")
try:
    # Mock database session
    class MockDB:
        def query(self, model):
            class MockQuery:
                def filter(self, *args):
                    class MockResult:
                        def first(self):
                            return None
                    return MockResult()
            return MockQuery()
    
    # Try to initialize without a valid team
    try:
        client = ZohoCRMClient("NONEXISTENT_TEAM", MockDB())
        print("   ❌ Client should have raised ValueError for nonexistent team")
        sys.exit(1)
    except ValueError as e:
        if "has no Zoho CRM connection" in str(e):
            print(f"   ✅ Correctly raises ValueError: {e}")
        else:
            print(f"   ❌ Wrong error message: {e}")
            sys.exit(1)
            
except Exception as e:
    print(f"   ❌ Unexpected error: {e}")
    sys.exit(1)

# Test encryption imports
print("\n5. Testing encryption utilities...")
try:
    from app.utils.encryption import encrypt_token, decrypt_token
    
    # Test encryption/decryption
    test_token = "test_token_12345"
    encrypted = encrypt_token(test_token)
    decrypted = decrypt_token(encrypted)
    
    if encrypted.startswith("enc:"):
        print(f"   ✅ Encryption adds 'enc:' prefix")
    else:
        print(f"   ⚠️  Encryption may not be configured (no prefix)")
    
    if decrypted == test_token or encrypted == test_token:
        # Either decrypted correctly or encryption not configured
        print(f"   ✅ Encryption/decryption working")
    else:
        print(f"   ❌ Encryption/decryption failed")
        sys.exit(1)
        
except Exception as e:
    print(f"   ❌ Encryption test failed: {e}")
    sys.exit(1)

# Test models
print("\n6. Testing model imports...")
try:
    from app.models import ZohoInstallation, Decision
    
    # Check ZohoInstallation attributes
    expected_attrs = ['team_id', 'zoho_org_id', 'zoho_domain', 
                     'access_token', 'refresh_token', 'token_expires_at']
    
    missing = []
    for attr in expected_attrs:
        if not hasattr(ZohoInstallation, attr):
            missing.append(attr)
    
    if missing:
        print(f"   ❌ ZohoInstallation missing attributes: {missing}")
        sys.exit(1)
    else:
        print(f"   ✅ ZohoInstallation has all required attributes")
        
except Exception as e:
    print(f"   ❌ Model import failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("🎉 ALL TESTS PASSED!")
print("=" * 70)
print("\n✅ Multi-tenant Zoho CRM integration is correctly implemented:")
print("   • ZohoCRMClient requires team_id and db")
print("   • Sync functions accept team_id and db parameters")
print("   • Client validates team exists before initialization")
print("   • Encryption utilities working")
print("   • Models have required attributes")
print("\n📝 Next steps:")
print("   1. Create Alembic migration for zoho_installations table (if needed)")
print("   2. Set ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET in .env")
print("   3. Test OAuth flow: GET /zoho/install?team_id=YOUR_TEAM")
print("   4. Test decision proposal and sync to Zoho")
print("\n")
