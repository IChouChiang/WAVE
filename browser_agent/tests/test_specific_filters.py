
import sys
import os
import time
from playwright.sync_api import sync_playwright

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_utils import launch_persistent_browser
from xhs_actions import search_xhs, apply_search_filters

def test_specific_filters():
    print("Starting Specific Filter Test...")
    
    with sync_playwright() as p:
        try:
            context, page = launch_persistent_browser(p, user_data_dir="./chrome_user_data")
            page.goto("https://www.xiaohongshu.com/explore")
            
            search_xhs(page, "Coffee")
            time.sleep(2)
            
            # Case 1: Time - '一天内' (Correct name)
            print("\n--- Testing Time: '一天内' ---")
            apply_search_filters(page, {"发布时间": "一天内"})
            
            # Case 2: Location - '附近'
            print("\n--- Testing Location: '附近' ---")
            apply_search_filters(page, {"位置距离": "附近"})
            
            # Case 3: Time - '最近一天' (Incorrect name, expected to fail)
            print("\n--- Testing Time: '最近一天' (Should fail) ---")
            apply_search_filters(page, {"发布时间": "最近一天"})

            print("\nTest completed.")
            context.close()
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_specific_filters()
