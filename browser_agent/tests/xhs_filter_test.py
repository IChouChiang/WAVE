"""
XHS Filter Functionality Test Script

This script verifies the search filter capabilities:
1. Performs an initial search.
2. Applies various filters:
   - Sort by Latest
   - Note Type (Video) + Time (Within a week)
   - Sort by Most Likes + Note Type (Image/Text)
   - Search Scope (Not Viewed)
   - Location Distance (Same City)
3. Verifies results after each filter application.
"""
import sys
import os
import time
from playwright.sync_api import sync_playwright

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_utils import launch_persistent_browser
from xhs_actions import search_xhs, extract_search_results, apply_search_filters

def main():
    print("Starting XHS Filter Test...")
    
    with sync_playwright() as p:
        try:
            context, page = launch_persistent_browser(p, user_data_dir="./chrome_user_data")
            page.goto("https://www.xiaohongshu.com/explore")
            
            # Initial Search
            search_xhs(page, "Python教程")
            extract_search_results(page, max_results=5)
            
            # Test 1: Sort by Latest
            print("\n--- Test 1: Sort by Latest ---")
            apply_search_filters(page, {"排序依据": "最新"})
            extract_search_results(page, max_results=5)
            
            # Test 2: Video + Within a week
            print("\n--- Test 2: Video + Within a week ---")
            apply_search_filters(page, {"笔记类型": "视频", "发布时间": "一周内"})
            extract_search_results(page, max_results=5)
            
            # Test 3: Most Likes + Image/Text
            print("\n--- Test 3: Most Likes + Image/Text ---")
            # Note: Changing sort might reset other filters, or they might persist. 
            # We'll just apply them and see.
            apply_search_filters(page, {"排序依据": "最多点赞", "笔记类型": "图文"})
            extract_search_results(page, max_results=5)

            # Test 4: Search Scope (Not Viewed)
            print("\n--- Test 4: Search Scope (Not Viewed) ---")
            apply_search_filters(page, {"搜索范围": "未看过"})
            extract_search_results(page, max_results=5)

            # Test 5: Location Distance (Same City)
            print("\n--- Test 5: Location Distance (Same City) ---")
            apply_search_filters(page, {"位置距离": "附近"})
            extract_search_results(page, max_results=5)
            
            print("\nTest completed. Press Enter to exit.")
            input()
            context.close()
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
