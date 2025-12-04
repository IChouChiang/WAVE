#!/usr/bin/env python3
"""
Integration test for Browser Agent configuration.
"""

import os
import sys

def test_config():
    """Test configuration module."""
    print("Testing configuration module...")
    
    # Temporarily set environment variable for testing
    os.environ['DEEPSEEK_API_KEY'] = 'test_key_for_validation'
    
    from config import config
    
    print(f"✓ Project root: {config.PROJECT_ROOT}")
    print(f"✓ Chrome user data dir: {config.get_chrome_user_data_dir()}")
    print(f"✓ XHS URL: {config.XHS_EXPLORE_URL}")
    print(f"✓ Browser headless: {config.BROWSER_HEADLESS}")
    
    # Test validation
    if config.validate():
        print("✓ Configuration validation passed")
    else:
        print("✗ Configuration validation failed")
        return False
    
    return True

def test_browser_utils():
    """Test browser utilities."""
    print("\nTesting browser utilities...")
    
    from browser_utils import get_ip_location
    
    location = get_ip_location()
    print(f"✓ IP location detection: {location}")
    
    return True

def test_imports():
    """Test all module imports."""
    print("\nTesting module imports...")
    
    modules = [
        'config',
        'browser_utils',
        'xhs_actions',
        'deepseek_agent',
        'xhs_mcp_server'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module} imports successfully")
        except ImportError as e:
            print(f"✗ {module} import failed: {e}")
            return False
    
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Browser Agent Integration Test")
    print("=" * 60)
    
    tests = [
        test_config,
        test_browser_utils,
        test_imports
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())