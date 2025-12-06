"""
Test script to simulate an LLM calling the XHS MCP tools.
This verifies that the tools work as expected when invoked programmatically.
"""
import sys
import os
import time


# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import settings as config

# Import the tools directly from the server file to simulate calls
# In a real scenario, an MCP client would call these over a protocol.
from xhs_mcp_server import launch_browser, search, get_search_results_list, open_post, get_post_details, close_post, filter_results

def main():
    print("--- Starting MCP Tool Simulation ---")
    
    # 1. Launch Browser
    print("\n[LLM] Calling launch_browser()...")
    result = launch_browser()
    print(f"[Tool Output]: {result}")
    
    if "Failed" in result:
        return

    try:
        # 2. Search
        print("\n[LLM] Calling search('DeepSeek')...")
        result = search("DeepSeek")
        print(f"[Tool Output]: {result}")
        
        # 3. Filter (Optional test)
        print("\n[LLM] Calling filter_results('排序依据', '最新')...")
        result = filter_results("排序依据", "最新")
        print(f"[Tool Output]: {result}")

        # 4. Get List
        print("\n[LLM] Calling get_search_results_list(max_results=3)...")
        result = get_search_results_list(max_results=3)
        print(f"[Tool Output]:\n{result}")
        
        # 5. Open Post
        print("\n[LLM] Calling open_post(0)...")
        result = open_post(0)
        print(f"[Tool Output]: {result}")
        
        # 6. Get Details
        print("\n[LLM] Calling get_post_details()...")
        result = get_post_details()
        print(f"[Tool Output]:\n{result}")
        
        # 7. Close Post
        print("\n[LLM] Calling close_post()...")
        result = close_post()
        print(f"[Tool Output]: {result}")
        
    except Exception as e:
        print(f"Simulation failed: {e}")
        
    print("\n--- Simulation Completed ---")
    print("Press Enter to exit (this will close the browser process if running via script)...")
    input()

if __name__ == "__main__":
    main()
