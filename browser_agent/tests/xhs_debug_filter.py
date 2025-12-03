"""
XHS Filter Component Debug Script

This utility script is designed to help developers inspect the dynamic filter component.
It navigates to the search page, opens the filter dropdown, and then triggers a 
browser debugger breakpoint (freezing the page) to allow for element inspection via DevTools.
"""
import sys
import os
import time
from playwright.sync_api import sync_playwright

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_utils import launch_persistent_browser
from xhs_actions import search_xhs

def main():
    print("Starting Debug Script for Filter Component...")
    
    with sync_playwright() as p:
        try:
            # Launch browser
            context, page = launch_persistent_browser(p, user_data_dir="./chrome_user_data")
            
            # 1. Navigate and Search to reveal the filter bar
            print("Navigating to XHS...")
            page.goto("https://www.xiaohongshu.com/explore")
            
            # We need to search to see the search-layout__top component
            search_xhs(page, "AI Agent")
            
            print("Waiting for the target filter element...")
            # User provided selector
            selector = "#global > div.main-container > div.with-side-bar.main-content > div > div > div.search-layout__top > clientonly > div > span"
            
            try:
                page.wait_for_selector(selector, timeout=10000)
                target_element = page.locator(selector).first
                
                print("Element found.")
                
                # 2. Interaction
                print("Hovering over the element...")
                target_element.hover()
                time.sleep(1)
                
                print("Clicking the element...")
                target_element.click()
                
                # Move mouse back over it just in case
                target_element.hover()
                
                print("\n!!! ACTION REQUIRED !!!")
                print("1. Open DevTools (F12) NOW if not already open.")
                print("2. The page will freeze (debugger breakpoint) in 3 seconds to let you inspect the dropdown.")
                
                # Inject a debugger statement that triggers after 3 seconds
                # This allows the user to open F12 and then the page freezes
                page.evaluate("setTimeout(() => { debugger; }, 3000)")
                
            except Exception as e:
                print(f"Could not find or interact with element: {e}")
                print("Trying a more generic selector for the filter dropdown if the specific one failed...")
                # Fallback logic could go here, but for now we stick to the request
            
            print("\nScript is paused. Press Enter in this terminal to close the browser.")
            input()
            
            context.close()
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
