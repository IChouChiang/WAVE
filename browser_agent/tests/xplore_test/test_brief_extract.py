"""
Brief test for the updated concise search_extract_xplore function.
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

def test_brief_extract():
    """
    Test the concise version of search_extract_xplore.
    """
    print("Testing concise IEEE Xplore extraction...")
    
    with sync_playwright() as p:
        try:
            context, page = launch_persistent_browser(p)
            
            # Navigate to IEEE Xplore
            page.goto("https://ieeexplore.ieee.org/Xplore/home.jsp")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Perform search
            search_query = "transformer models"
            print(f"Searching for: '{search_query}'")
            search_xplore(page, search_query)
            
            # Wait for results
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # Extract results (concise version)
            print("\nExtracting search results (concise output)...")
            results_info = search_extract_xplore(page)
            
            # Show only the final result
            print(f"\n✅ Result: {results_info}")
            
            # Quick info
            print(f"\nPage URL: {page.url}")
            print(f"Page title: {page.title()}")
            
            print("\nPress Enter to close browser...")
            input()
            
            context.close()
            print("✓ Test completed")
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_brief_extract()