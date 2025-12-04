"""
Debug script for Filter Tool.
"""
import sys
import os
import time


# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

from xhs_mcp_server import launch_browser, search, filter_results

def main():
    print("--- Starting Filter Debug ---")
    
    print("\n1. Launching Browser...")
    print(launch_browser())
    
    print("\n2. Searching for 'DeepSeek'...")
    print(search("DeepSeek"))
    
    print("\n3. Waiting 5 seconds for page to settle...")
    time.sleep(5)
    
    print("\n4. Attempting to apply filter: 排序依据 = 最新")
    
    # Custom debug logic to inspect page before/after click
    # We can't easily modify the imported function, so we will rely on the function's output
    # but we can add a step to dump html if we were using the browser object directly.
    # Since we are using the mcp server functions, we have to trust them or modify them.
    
    result = filter_results("排序依据", "最新")
    print(f"[Result]: {result}")
    
    print("\n--- Debug Pause ---")
    print("Browser is open. Please inspect the UI.")
    print("Check if the filter dropdown is visible or if the button was clicked.")
    print("Press Enter to exit...")
    input()

if __name__ == "__main__":
    main()
