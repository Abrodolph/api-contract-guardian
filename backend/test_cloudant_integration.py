"""
Test script to verify Cloudant integration with in-memory fallback.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("Testing Cloudant Integration")
print("=" * 60)

# Test 1: Import cloudant_store module
print("\n1. Testing cloudant_store import...")
try:
    from cloud import cloudant_store
    print("   [OK] Module imported successfully")
except Exception as e:
    print(f"   [FAIL] Import failed: {e}")
    sys.exit(1)

# Test 2: Check Cloudant availability
print("\n2. Checking Cloudant availability...")
is_available = cloudant_store.is_cloudant_available()
print(f"   Cloudant available: {is_available}")
if not is_available:
    print("   [INFO] This is expected without CLOUDANT_URL env var")

# Test 3: Import backend main module
print("\n3. Testing backend main.py import...")
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
    import main
    print("   [OK] Backend module imported successfully")
    print(f"   CLOUDANT_AVAILABLE flag: {main.CLOUDANT_AVAILABLE}")
except Exception as e:
    print(f"   [FAIL] Import failed: {e}")
    sys.exit(1)

# Test 4: Verify in-memory store still works
print("\n4. Testing in-memory store fallback...")
try:
    print(f"   In-memory store has {len(main._store)} seed documents")
    if len(main._store) > 0:
        print("   [OK] Seed data loaded correctly")
    else:
        print("   [FAIL] No seed data found")
except Exception as e:
    print(f"   [FAIL] Error accessing store: {e}")

# Test 5: Check new endpoint exists
print("\n5. Checking new /health/contract endpoint...")
try:
    # Check if the function exists
    if hasattr(main, 'get_contract_health'):
        print("   [OK] get_contract_health() function exists")
    else:
        print("   [FAIL] get_contract_health() function not found")
except Exception as e:
    print(f"   [FAIL] Error: {e}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
print("\nTo test with Cloudant:")
print("1. Set environment variables:")
print("   - CLOUDANT_URL")
print("   - CLOUDANT_API_KEY")
print("   - CLOUDANT_DB_NAME (optional, defaults to 'verdicts')")
print("2. Run this test again")
print("\nTo start the server:")
print("   cd backend")
print("   python main.py")

# Made with Bob
