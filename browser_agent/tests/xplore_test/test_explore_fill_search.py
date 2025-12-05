"""
Test file for IEEE Xplore search functionality.
Tests the basic search box filling action.
"""

import sys
import os
import time
from playwright.sync_api import sync_playwright

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import config
from browser_utils import launch_persistent_browser
from xplore_actions import search_xplore

def test_xplore_search():
    """
    Test the IEEE Xplore search functionality.
    
    Steps:
    1. Launch browser with stealth settings
    2. Navigate to IEEE Xplore homepage
    3. Fill search box with query
    4. Submit search
    5. Wait for user to press Enter to exit
    """
    print("Starting IEEE Xplore search test...")
    
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
            
            # Take initial screenshot
            initial_screenshot = "test_xplore_initial.png"
            page.screenshot(path=initial_screenshot)
            print(f"  Initial screenshot: {initial_screenshot}")
            
            # Test search functionality - DON'T submit search yet
            search_query = "Power Flow Methods Extended by Node Types"
            print(f"\n--- Testing search with query: '{search_query}' ---")
            search_xplore(page, search_query, submit_search=False)
            
            # Take a screenshot to verify the input is filled
            print("\nTaking screenshot to verify input...")
            screenshot_path = "test_xplore_search.png"
            page.screenshot(path=screenshot_path)
            print(f"✓ Screenshot saved to: {screenshot_path}")
            
            # Wait for user to manually verify
            print("\n" + "="*60)
            print("IMPORTANT: Browser is now open with search box filled.")
            print("Please verify:")
            print("1. Can you see the text in the search box?")
            print("2. Is it 'Power Flow Methods Extended by Node Types'?")
            print("3. You can manually press Enter in the browser to submit search.")
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
    test_xplore_search()