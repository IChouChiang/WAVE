"""
Test file for IEEE Xplore search results extraction functionality.
Tests the search_extract_xplore function.
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

def test_xplore_extract():
    """
    Test the IEEE Xplore search results extraction functionality.
    
    Steps:
    1. Launch browser with stealth settings
    2. Navigate to IEEE Xplore homepage
    3. Perform a search
    4. Extract and display search results information
    5. Wait for user to press Enter to exit
    """
    print("Starting IEEE Xplore search results extraction test...")
    
    with sync_playwright() as p:
        try:
            # Launch browser with persistent context
            context, page = launch_persistent_browser(p)
            
            # Navigate to IEEE Xplore homepage
            print("Navigating to IEEE Xplore homepage...")
            page.goto("https://ieeexplore.ieee.org/Xplore/home.jsp")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Check page title and URL
            page_title = page.title()
            current_url = page.url
            print(f"✓ Page loaded successfully")
            print(f"  Title: {page_title}")
            print(f"  URL: {current_url}")
            
            # Perform search
            search_query = "Power Flow Methods Extended by Node Types"
            print(f"\n--- Performing search: '{search_query}' ---")
            search_xplore(page, search_query)
            
            # Wait for search results to load
            print("Waiting for search results to load...")
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            
            # Check if we're on search results page
            current_url = page.url
            page_title = page.title()
            print(f"✓ Search submitted")
            print(f"  Current URL: {current_url}")
            print(f"  Page title: {page_title}")
            
            # Extract search results information
            print("\n--- Extracting search results information ---")
            results_info = search_extract_xplore(page)
            print(f"\nExtracted results: {results_info}")
            
            # Wait for user to manually verify
            print("\n" + "="*60)
            print("IMPORTANT: Browser is now open with search results.")
            print("Please verify:")
            print("1. Did the search work correctly?")
            print("2. Are you on the search results page?")
            print("3. Does the extracted information match what you see in the browser?")
            print(f"4. Extracted info: {results_info}")
            print("\nPress Enter in THIS terminal to close the browser...")
            print("="*60)
            input()
            
            # Close browser
            print("Closing browser...")
            context.close()
            print("✓ Browser closed")
            
        except Exception as e:
            print(f"An error occurred during test: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_xplore_extract()