"""
Simple test for IEEE Xplore search results extraction with different query.
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

def test_simple_extract():
    """
    Test with a simpler search query.
    """
    print("Testing IEEE Xplore extraction with simple query...")
    
    with sync_playwright() as p:
        try:
            context, page = launch_persistent_browser(p)
            
            # Navigate to IEEE Xplore
            page.goto("https://ieeexplore.ieee.org/Xplore/home.jsp")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Perform search with simple query
            search_query = "machine learning"
            print(f"\nSearching for: '{search_query}'")
            search_xplore(page, search_query)
            
            # Wait for results
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # Extract results
            print("\nExtracting search results...")
            results_info = search_extract_xplore(page)
            print(f"\n✅ Extracted: {results_info}")
            
            # Quick verification
            print("\n" + "="*60)
            print("Quick verification:")
            print(f"1. URL: {page.url}")
            print(f"2. Title: {page.title()}")
            print(f"3. Extracted info: {results_info}")
            print("\nPress Enter to close browser...")
            print("="*60)
            input()
            
            context.close()
            print("✓ Test completed")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_simple_extract()