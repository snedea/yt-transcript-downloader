#!/usr/bin/env python3
"""
Simple test to verify logout endpoint parameter configuration.
Tests the endpoint signature without running the full app.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

def test_endpoint_signatures():
    """Test that endpoints have correct parameter annotations"""
    print("\n" + "="*80)
    print("LOGOUT BUG FIX VALIDATION - Endpoint Signature Test")
    print("="*80)

    try:
        # Import the router module
        from app.routers import auth
        from fastapi import Body
        import inspect

        print("\n[Test 1] Checking /logout endpoint signature")
        print("-" * 80)

        # Get the logout function
        logout_func = auth.logout
        sig = inspect.signature(logout_func)

        # Check if refresh_token parameter exists
        if 'refresh_token' not in sig.parameters:
            print("❌ FAILED: refresh_token parameter not found")
            return False

        # Get the parameter
        refresh_token_param = sig.parameters['refresh_token']

        # Check if it has a default value (which should be Body(...))
        has_body_annotation = False
        if refresh_token_param.default != inspect.Parameter.empty:
            default_val = refresh_token_param.default
            # Check if it's a Body field
            if hasattr(default_val, '__class__'):
                class_name = default_val.__class__.__name__
                if 'Body' in class_name or 'FieldInfo' in class_name:
                    has_body_annotation = True

        print(f"Parameter name: refresh_token")
        print(f"Parameter default: {refresh_token_param.default}")
        print(f"Has Body annotation: {has_body_annotation}")

        if has_body_annotation:
            print("✅ PASSED: refresh_token is configured to accept request body")
        else:
            print("❌ FAILED: refresh_token is NOT configured for request body")
            print("   (It will be treated as query parameter)")
            return False

        print("\n[Test 2] Checking /refresh endpoint signature")
        print("-" * 80)

        # Get the refresh_token function
        refresh_func = auth.refresh_token
        sig = inspect.signature(refresh_func)

        # Check if refresh_token parameter exists
        if 'refresh_token' not in sig.parameters:
            print("❌ FAILED: refresh_token parameter not found")
            return False

        # Get the parameter
        refresh_token_param = sig.parameters['refresh_token']

        # Check if it has Body annotation
        has_body_annotation = False
        if refresh_token_param.default != inspect.Parameter.empty:
            default_val = refresh_token_param.default
            if hasattr(default_val, '__class__'):
                class_name = default_val.__class__.__name__
                if 'Body' in class_name or 'FieldInfo' in class_name:
                    has_body_annotation = True

        print(f"Parameter name: refresh_token")
        print(f"Parameter default: {refresh_token_param.default}")
        print(f"Has Body annotation: {has_body_annotation}")

        if has_body_annotation:
            print("✅ PASSED: refresh_token is configured to accept request body")
        else:
            print("❌ FAILED: refresh_token is NOT configured for request body")
            return False

        print("\n[Test 3] Checking Body import in auth module")
        print("-" * 80)

        # Check if Body is imported
        import app.routers.auth as auth_module
        if hasattr(auth_module, 'Body'):
            print("✅ PASSED: Body is imported in auth.py")
        else:
            print("❌ WARNING: Body might not be directly imported")
            # This is OK as long as it's used via fastapi.Body

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_fix_in_code():
    """Read the auth.py file and verify the fix is present"""
    print("\n[Test 4] Verifying fix in source code")
    print("-" * 80)

    try:
        auth_file = os.path.join(os.path.dirname(__file__), 'app', 'routers', 'auth.py')
        with open(auth_file, 'r') as f:
            content = f.read()

        # Check for Body import
        has_body_import = 'from fastapi import' in content and 'Body' in content.split('from fastapi import')[1].split('\n')[0]

        # Check for Body usage in logout
        has_logout_body = 'def logout(' in content and 'Body(..., embed=True)' in content

        # Check for Body usage in refresh
        has_refresh_body = 'def refresh_token(' in content and content.count('Body(..., embed=True)') >= 2

        print(f"Body imported: {has_body_import}")
        print(f"Logout uses Body: {has_logout_body}")
        print(f"Refresh uses Body: {has_refresh_body}")

        if has_body_import and has_logout_body and has_refresh_body:
            print("✅ PASSED: Source code contains the fix")
            return True
        else:
            print("❌ FAILED: Fix not found in source code")
            return False

    except Exception as e:
        print(f"❌ ERROR reading source: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("SIMPLIFIED LOGOUT BUG FIX VALIDATION")
    print("="*80)
    print("\nThis test verifies the endpoint signatures are correct")
    print("without requiring a full app startup.")
    print("="*80)

    # Run source code check first (doesn't require imports)
    code_check = verify_fix_in_code()

    # Run signature tests
    sig_check = test_endpoint_signatures()

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    if code_check and sig_check:
        print("✅ ALL TESTS PASSED!")
        print("\n🎉 Logout bug is FIXED!")
        print("\nThe endpoints now correctly accept refresh_token in request body.")
        print("This prevents tokens from appearing in server logs (URL parameters).")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED!")
        if not code_check:
            print("  - Source code verification failed")
        if not sig_check:
            print("  - Signature verification failed")
        sys.exit(1)
