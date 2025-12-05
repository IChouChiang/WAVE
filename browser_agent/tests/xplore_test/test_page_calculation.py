#!/usr/bin/env python3
"""
Quick test to verify page calculation in search_extract_xplore.
"""
import sys
import os
import time
from playwright.sync_api import sync_playwright

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import config
from browser_utils import launch_persistent_browser
from xplore_actions import search_xplore, search_extract_xplore

def test_page_calculation():
    """Test that page calculation appears in output."""
    print("Testing page calculation in search_extract_xplore...")
    
    with sync_playwright() as p:
        context = None
        try:
            context, page = launch_persistent_browser(p)
            
            # Navigate to IEEE Xplore
            page.goto("https://ieeexplore.ieee.org/Xplore/home.jsp")
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # Search for a term
            search_query = "machine learning"
            print(f"Searching for: '{search_query}'")
            search_xplore(page, search_query)
            
            # Wait for results
            page.wait_for_load_state("networkidle")
            time.sleep(6)
            
            # Extract first 3 results
            print("\nExtracting first 3 results (should show page info):")
            print("-" * 60)
            result = search_extract_xplore(page, start_index=1, end_index=3)
            print(result)
            
            # Check if page info appears
            if "Page 1 of" in result and "up to 25 results per page" in result:
                print("\n✓ SUCCESS: Page calculation appears in output")
            else:
                print("\n✗ FAILED: Page calculation missing from output")
                
        finally:
            if context:
                input("\nPress Enter to close browser...")
                context.close()

if __name__ == "__main__":
    test_page_calculation()