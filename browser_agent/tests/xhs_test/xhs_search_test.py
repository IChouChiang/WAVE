"""
XHS Search & Extraction Test Script

This script demonstrates the core workflow of the browser agent:
1. Launches a persistent browser session.
2. Performs searches on Xiaohongshu.
3. Extracts search results (titles and likes).
4. Navigates to specific posts, extracts detailed content (text, tags, stats, comments), and closes the modal.
"""
import sys
import os
import time
from playwright.sync_api import sync_playwright

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from browser_utils import launch_persistent_browser
from xhs_actions import search_xhs, extract_search_results, extract_post_details, close_post_details

def main():
    print("Starting XHS Search Test...")
    
    with sync_playwright() as p:
        try:
            # Launch browser using the utility function
            context, page = launch_persistent_browser(p)
            
            # 1. Navigate to Explore page
            from config import config
            url = config.XHS_EXPLORE_URL
            print(f"Navigating to {url}...")
            page.goto(url)
            page.wait_for_load_state("domcontentloaded")
            
            # 2. First Search
            search_xhs(page, "AI Agent开发教程")
            extract_search_results(page)
            time.sleep(3) # Let user see the result
            
            # 3. Second Search (Testing clear functionality)
            search_xhs(page, "Cursor使用技巧")
            extract_search_results(page)
            
            # 4. Click the 3rd post (Index 2)
            print("\nClicking the 3rd post to open details...")
            try:
                # The cover is the clickable image area defined by class "cover"
                target_cover = page.locator(".cover").nth(2)
                target_cover.wait_for(state="visible", timeout=5000)
                target_cover.click()
                print("Clicked 3rd post.")
                
                # Wait a bit to see the effect (modal opening)
                time.sleep(5)
                print("Detail view should be open now.")

                # 5. Extract Details (Text, Tags, Stats)
                extract_post_details(page)
                
                # 6. Close Details
                close_post_details(page)
                
                # 7. Click the 4th post (Index 3)
                print("\nClicking the 4th post to open details...")
                target_cover_4 = page.locator(".cover").nth(3)
                target_cover_4.wait_for(state="visible", timeout=5000)
                target_cover_4.click()
                print("Clicked 4th post.")
                
                time.sleep(5)
                extract_post_details(page)
                close_post_details(page)
                
            except Exception as e:
                print(f"Failed to interact with post details: {e}")
            
            print("Test completed successfully.")
            print("Browser remains open for monitoring. Press Enter to close the browser and exit...")
            input()
            
            context.close()
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
