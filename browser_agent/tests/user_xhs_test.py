"""
User Browser XHS Search Test

This script connects to the running "Bot Browser" (port 9223) and attempts to 
search Xiaohongshu (XHS) to verify that the login session is active and stealth works.
"""
import sys
import os
import time
from playwright.sync_api import sync_playwright

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the new user browser utility
from user_browser_utils import launch_user_browser
from config import settings as config

def main():
    print("============================================================")
    print("USER BROWSER XHS SEARCH TEST")
    print("============================================================")
    print("1. Ensure 'launch_debug_chrome.ps1' is running.")
    print("2. Ensure you are LOGGED IN to Xiaohongshu in that window.")
    print("============================================================")
    
    with sync_playwright() as p:
        try:
            # Connect to the existing browser
            context, page = launch_user_browser(p, headless=False)
            
            # Navigate to XHS Explore
            target_url = "https://www.xiaohongshu.com/explore"
            print(f"Navigating to: {target_url}")
            page.goto(target_url)
            page.wait_for_load_state("domcontentloaded")
            
            # Check for login indicator
            # Look for user avatar or specific logged-in elements
            print("Checking login status...")
            try:
                # The "Me" or avatar element usually indicates login
                # This selector might need adjustment based on XHS updates
                avatar = page.locator(".user-side-content").first
                if avatar.is_visible(timeout=3000):
                    print("✅ Login detected (User side content visible).")
                else:
                    print("⚠️  Warning: Could not definitively confirm login status (Avatar not found).")
            except:
                print("⚠️  Warning: Login check timed out.")

            # Perform a search
            search_keyword = "AI Agent"
            print(f"Searching for: {search_keyword}")
            
            # Locate search input
            search_input = page.locator("input#search-input").first
            if not search_input.is_visible():
                # Try alternative selector
                search_input = page.get_by_placeholder("搜索小红书").first
            
            if search_input.is_visible():
                # Clear existing text if any
                search_input.click()
                search_input.fill("")
                time.sleep(0.5)
                
                search_input.fill(search_keyword)
                page.keyboard.press("Enter")
                print("Search submitted.")
                
                # Wait for results
                print("Waiting for results...")
                # Wait for the feed container to be visible
                page.wait_for_selector(".feeds-container", timeout=10000)
                
                # Wait a bit more for items to populate
                time.sleep(3)
                
                # Count results
                results = page.locator(".feeds-container .note-item")
                count = results.count()
                print(f"✅ Found {count} results for '{search_keyword}'.")
                
                if count == 0:
                    print("⚠️  No results found immediately. Waiting 3 more seconds...")
                    time.sleep(3)
                    count = results.count()
                    print(f"   Re-check: Found {count} results.")
                
                if count > 0:
                    first_title = results.first.locator(".footer .title").inner_text()
                    print(f"First result title: {first_title}")
                    
                    # --- NEW: Click into the first result to verify detail page access ---
                    print("\n--- Verifying Detail Page Access ---")
                    print("Clicking first result...")
                    
                    # Get the first result element
                    first_result = results.first
                    
                    # Click it (this usually opens a modal or new page)
                    first_result.click()
                    
                    # Wait for detail container to appear
                    # XHS usually opens details in a modal overlay with class .note-detail-mask or .note-container
                    print("Waiting for detail view...")
                    try:
                        # Wait for either the modal mask or the note content
                        page.wait_for_selector(".note-detail-mask, .note-container", timeout=8000)
                        print("✅ Detail view opened successfully.")
                        
                        # Extract some detail info to prove we can read it
                        # Title in detail view
                        detail_title = page.locator("#detail-title, .note-content .title").first
                        if detail_title.is_visible():
                            print(f"Detail Page Title: {detail_title.inner_text()}")
                        
                        # Extract author name
                        author = page.locator(".author-container .name").first
                        if author.is_visible():
                            print(f"Author: {author.inner_text()}")
                            
                        # Extract like count
                        likes = page.locator(".interact-container .like-wrapper .count").first
                        if likes.is_visible():
                            print(f"Likes: {likes.inner_text()}")
                            
                        # Close the detail view (click the close button or mask)
                        print("Closing detail view...")
                        close_btn = page.locator(".close-circle, .close-mask").first
                        if close_btn.is_visible():
                            close_btn.click()
                        else:
                            # Click outside (on the mask)
                            page.locator(".note-detail-mask").click(position={"x": 10, "y": 10})
                            
                        print("✅ Returned to feed.")
                        
                    except Exception as e:
                        print(f"❌ Failed to load detail view: {e}")
                    
            else:
                print("❌ Could not find search input box.")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
