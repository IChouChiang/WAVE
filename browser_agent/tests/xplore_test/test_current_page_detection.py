#!/usr/bin/env python3
"""
Test current page detection from pagination UI.
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

def test_current_page_detection():
    """Test that current page is detected from pagination UI."""
    print("Testing current page detection from pagination...")
    
    with sync_playwright() as p:
        context = None
        try:
            context, page = launch_persistent_browser(p)
            
            # Navigate to IEEE Xplore
            print("Navigating to IEEE Xplore...")
            page.goto("https://ieeexplore.ieee.org/Xplore/home.jsp")
            page.wait_for_load_state("domcontentloaded")
            time.sleep(3)
            
            # Search for "opf flow machine learning" (fewer results)
            search_query = "opf flow machine learning"
            print(f"Searching for: '{search_query}'")
            search_xplore(page, search_query)
            
            # Wait for results with timeout
            try:
                page.wait_for_load_state("domcontentloaded", timeout=15000)
            except:
                print("Timeout waiting for domcontentloaded, continuing...")
            time.sleep(5)
            
            # Extract first 3 results
            print("\nExtracting first 3 results (should show page info):")
            print("-" * 60)
            result = search_extract_xplore(page, start_index=1, end_index=3)
            print(result)
            
            # Check if page info appears
            if "Page 1 of" in result and "up to 25 results per page" in result:
                print("\n✓ SUCCESS: Page calculation appears in output")
                
                # Try to navigate to page 2 if available
                print("\nChecking if we can detect pagination UI...")
                try:
                    pagination_selector = "#xplMainContent > div.ng-SearchResults.row.g-0 > div.col > xpl-paginator > div.pagination-bar.hide-mobile.text-base-md-lh > ul"
                    pagination_list = page.locator(pagination_selector).first
                    if pagination_list.is_visible():
                        print("✓ Pagination UI found")
                        
                        # Count pagination buttons
                        buttons = pagination_list.locator("button").all()
                        print(f"  Found {len(buttons)} pagination buttons")
                        
                        # Find active button
                        active_button = pagination_list.locator("button.active").first
                        if active_button.is_visible():
                            page_num = active_button.inner_text().strip()
                            print(f"  Active page button shows: '{page_num}'")
                            
                        # Check if there's a next page button
                        next_button = pagination_list.locator("button.stats-Pagination_arrow_next_2").first
                        if next_button.is_visible():
                            print("  Next page button available")
                            
                            # Click next page to test page 2 detection
                            print("  Clicking next page...")
                            next_button.click()
                            
                            # Wait for page 2 to load
                            try:
                                page.wait_for_load_state("domcontentloaded", timeout=15000)
                            except:
                                print("Timeout waiting for page 2, continuing...")
                            time.sleep(5)
                            
                            # Extract results from page 2
                            print("\nExtracting first 3 results from page 2:")
                            print("-" * 60)
                            result_page2 = search_extract_xplore(page, start_index=1, end_index=3)
                            print(result_page2)
                            
                            if "Page 2 of" in result_page2:
                                print("\n✓ SUCCESS: Correctly detected page 2")
                            else:
                                print("\n✗ FAILED: Page 2 not detected")
                    else:
                        print("✗ Pagination UI not visible")
                except Exception as e:
                    print(f"✗ Error checking pagination: {e}")
            else:
                print("\n✗ FAILED: Page calculation missing from output")
                
        finally:
            if context:
                input("\nPress Enter to close browser...")
                context.close()

if __name__ == "__main__":
    test_current_page_detection()