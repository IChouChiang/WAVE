
import sys
import os
import time
from playwright.sync_api import sync_playwright

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_utils import launch_persistent_browser
from xhs_actions import search_xhs

def inspect_filters():
    print("Starting Filter Inspection...")
    
    with sync_playwright() as p:
        try:
            context, page = launch_persistent_browser(p, user_data_dir="./chrome_user_data")
            page.goto("https://www.xiaohongshu.com/explore")
            
            # Initial Search
            search_xhs(page, "Python")
            time.sleep(3) # Wait for results
            
            # Try to open filter dropdown
            print("Attempting to open filter dropdown...")
            
            # Try selectors from xhs_actions.py
            filter_btn_selectors = [
                ".search-layout__top clientonly > div > span", 
                ".filter-box", 
                ".filter-icon", 
                "text=综合", 
                "text=筛选"
            ]
            
            dropdown_opened = False
            for selector in filter_btn_selectors:
                try:
                    if page.locator(selector).first.is_visible():
                        print(f"Clicking {selector}")
                        page.locator(selector).first.click()
                        try:
                            page.wait_for_selector(".filters-wrapper", state="visible", timeout=3000)
                            print("Dropdown opened!")
                            dropdown_opened = True
                            break
                        except:
                            print("Dropdown did not appear.")
                except:
                    pass
            
            if not dropdown_opened:
                print("Failed to open dropdown. Exiting.")
                return

            # Inspect categories and options
            print("\n--- Available Filters ---")
            filter_rows = page.locator(".filters-wrapper .filters").all()
            
            for row in filter_rows:
                cat_span = row.locator("span").first
                if cat_span.is_visible():
                    category = cat_span.inner_text()
                    print(f"\nCategory: [{category}]")
                    
                    tags = row.locator(".tags").all()
                    options = [tag.inner_text().strip() for tag in tags]
                    print(f"Options: {options}")
            
            print("\n-------------------------")
            
            input("Press Enter to close...")
            context.close()
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    inspect_filters()
