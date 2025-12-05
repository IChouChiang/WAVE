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
            
            # Initial page loaded successfully
            
            # Test search functionality - will automatically click search button
            search_query = "Power Flow Methods Extended by Node Types"
            print(f"\n--- Testing search with query: '{search_query}' ---")
            search_xplore(page, search_query)
            
            # Wait for search results to load
            print("Waiting for search results to load...")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Check if we're on search results page
            current_url = page.url
            page_title = page.title()
            print(f"✓ Search submitted")
            print(f"  Current URL: {current_url}")
            print(f"  Page title: {page_title}")
            
            # Search results page loaded
            
            # Check for search results
            print("\nChecking for search results...")
            
            # Try to find search result elements
            try:
                # Look for result count or result items
                result_count = page.locator("xpl-results-count").first
                if result_count.is_visible():
                    count_text = result_count.text_content()
                    print(f"  Search result count: {count_text}")
                else:
                    print("  No result count element found")
                    
                # Look for individual result items
                result_items = page.locator("xpl-results-item").all()
                if result_items:
                    print(f"  Found {len(result_items)} result items")
                    
                    # Show first few results
                    for i in range(min(3, len(result_items))):
                        try:
                            title_elem = result_items[i].locator("h2 a").first
                            if title_elem.is_visible():
                                title = title_elem.text_content()
                                print(f"  Result {i+1}: {title[:80]}...")
                        except:
                            pass
                else:
                    print("  No result items found")
                    
            except Exception as e:
                print(f"  Error checking results: {e}")
            
            # --- SECOND SEARCH TEST ---
            print("\n" + "="*60)
            print("Testing second search from results page...")
            print("="*60)
            
            # Wait a moment for page to stabilize
            time.sleep(2)
            
            # Perform second search with different keywords
            second_search_query = "machine learning transformer models"
            print(f"\n--- Performing second search: '{second_search_query}' ---")
            
            # The search box should be empty on results page, so we can reuse search_xplore
            search_xplore(page, second_search_query)
            
            # Wait for second search results to load
            print("Waiting for second search results to load...")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Check second search results
            current_url = page.url
            page_title = page.title()
            print(f"✓ Second search submitted")
            print(f"  Current URL: {current_url}")
            print(f"  Page title: {page_title}")
            
            # Check for second search results
            print("\nChecking for second search results...")
            try:
                # Look for result count again
                result_count = page.locator("xpl-results-count").first
                if result_count.is_visible():
                    count_text = result_count.text_content()
                    print(f"  Second search result count: {count_text}")
                else:
                    print("  No result count element found for second search")
                    
                # Look for individual result items
                result_items = page.locator("xpl-results-item").all()
                if result_items:
                    print(f"  Found {len(result_items)} result items in second search")
                    
                    # Show first few results
                    for i in range(min(3, len(result_items))):
                        try:
                            title_elem = result_items[i].locator("h2 a").first
                            if title_elem.is_visible():
                                title = title_elem.text_content()
                                print(f"  Result {i+1}: {title[:80]}...")
                        except:
                            pass
                else:
                    print("  No result items found in second search")
                    
            except Exception as e:
                print(f"  Error checking second results: {e}")
            
            # Wait for user to manually verify
            print("\n" + "="*60)
            print("IMPORTANT: Browser is now open with SECOND search results.")
            print("Please verify:")
            print("1. Did the first search work correctly?")
            print("2. Did the second search from results page work?")
            print("3. Can you see search results for 'machine learning transformer models'?")
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