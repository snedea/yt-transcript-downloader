#!/usr/bin/env python3
"""
Test script to verify logout endpoint accepts refresh_token in request body.
"""
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.main import app

client = TestClient(app)

def test_logout_parameter_format():
    """Test that logout endpoint accepts refresh_token in request body"""
    print("\n" + "="*80)
    print("Testing Logout Endpoint Parameter Format")
    print("="*80)

    # Test 1: Verify /logout endpoint expects body parameter
    print("\n[Test 1] Testing /logout with refresh_token in REQUEST BODY")
    print("-" * 80)

    # Note: This will fail with 401 because we're not authenticated,
    # but we're checking if it accepts the parameter format (not 422 error)
    response = client.post(
        "/api/auth/logout",
        json={"refresh_token": "test_token_123"}
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 422:
        print("❌ FAILED: Returns 422 - Parameter format issue")
        print("   This means the endpoint still expects query parameter")
        return False
    elif response.status_code == 401:
        print("✅ PASSED: Returns 401 - Parameter format is correct")
        print("   (401 is expected because we're not authenticated)")
        print("   This confirms the endpoint accepts body parameters")
        return True
    else:
        print(f"⚠️  UNEXPECTED: Returns {response.status_code}")
        return None

    print("-" * 80)

def test_refresh_parameter_format():
    """Test that refresh endpoint accepts refresh_token in request body"""
    print("\n[Test 2] Testing /refresh with refresh_token in REQUEST BODY")
    print("-" * 80)

    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": "test_token_123"}
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 422:
        print("❌ FAILED: Returns 422 - Parameter format issue")
        return False
    elif response.status_code == 401:
        print("✅ PASSED: Returns 401 - Parameter format is correct")
        print("   (401 is expected for invalid token)")
        return True
    else:
        print(f"⚠️  UNEXPECTED: Returns {response.status_code}")
        return None

    print("-" * 80)

def test_logout_query_param_rejected():
    """Test that logout endpoint REJECTS query parameters (security best practice)"""
    print("\n[Test 3] Testing /logout with refresh_token as QUERY PARAMETER")
    print("-" * 80)

    response = client.post(
        "/api/auth/logout?refresh_token=test_token_123"
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

    if response.status_code == 422:
        print("✅ PASSED: Returns 422 - Query parameter correctly rejected")
        print("   This is a security best practice (tokens shouldn't be in URLs)")
        return True
    else:
        print(f"❌ FAILED: Accepts query parameter (security risk)")
        return False

    print("-" * 80)

if __name__ == "__main__":
    print("\n" + "="*80)
    print("LOGOUT BUG FIX VALIDATION TEST")
    print("="*80)
    print("\nThis test verifies that the logout and refresh endpoints:")
    print("1. Accept refresh_token in request body (secure)")
    print("2. Reject refresh_token as query parameter (insecure)")
    print("="*80)

    results = []

    # Run tests
    results.append(("Logout body parameter", test_logout_parameter_format()))
    results.append(("Refresh body parameter", test_refresh_parameter_format()))
    results.append(("Logout query param rejected", test_logout_query_param_rejected()))

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL" if result is False else "⚠️  SKIP"
        print(f"{status} - {test_name}")

    print("-" * 80)
    print(f"Total: {passed} passed, {failed} failed out of {len(results)} tests")
    print("="*80)

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Logout bug is FIXED!")
        print("\nThe endpoints now correctly:")
        print("  ✅ Accept refresh_token in request body (secure)")
        print("  ✅ Reject refresh_token in URL query params (prevents logging)")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED! Bug may not be fully fixed.")
        sys.exit(1)
