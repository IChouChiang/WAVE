
import sys
import os
import time
from playwright.sync_api import sync_playwright

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_utils import launch_persistent_browser
from xhs_actions import search_xhs

def debug_location_html():
    print("Starting Location HTML Debug...")
    
    with sync_playwright() as p:
        try:
            context, page = launch_persistent_browser(p, user_data_dir="./chrome_user_data")
            page.goto("https://www.xiaohongshu.com/explore")
            
            search_xhs(page, "Coffee")
            time.sleep(2)
            
            print("Opening filter dropdown...")
            try:
                page.locator(".filter-icon").click()
                page.wait_for_selector(".filters-wrapper", state="visible", timeout=3000)
            except:
                page.locator(".search-layout__top clientonly > div > span").click()
                page.wait_for_selector(".filters-wrapper", state="visible", timeout=3000)
            
            time.sleep(1)
            
            # Find the location row
            rows = page.locator(".filters-wrapper .filters").all()
            loc_row = None
            for row in rows:
                if "位置距离" in row.inner_text():
                    loc_row = row
                    break
            
            if loc_row:
                print("\n--- Location Row HTML ---")
                print(loc_row.inner_html())
                print("-------------------------")
                
                # Try to find the specific options
                tags = loc_row.locator(".tag-container > div").all()
                print(f"\nFound {len(tags)} tags in container.")
                for i, tag in enumerate(tags):
                    print(f"Tag {i+1}: Text='{tag.inner_text()}', Class='{tag.get_attribute('class')}'")
            else:
                print("Location row not found!")

            print("\nDebug completed. Press Enter to exit.")
            input()
            context.close()
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    debug_location_html()
