
import sys
import os
import time

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the functions directly from the MCP server file
# Note: This will execute the module-level code in xhs_mcp_server.py, 
# including creating the FastMCP instance, which is fine.
from xhs_mcp_server import launch_browser, search, filter_results, get_search_results_list, state
from xhs_actions import apply_search_filters

def test_mcp_tools():
    print("--- Testing MCP Tools Directly (Expanded) ---")
    
    # 1. Launch Browser
    print("\n[1] Calling launch_browser()...")
    launch_browser()
    
    if not state.page:
        print("Error: Browser state not initialized.")
        return

    # 2. Search - Changing keyword to '美食' (Food)
    query = "美食"
    print(f"\n[2] Calling search('{query}')...")
    search(query)
    time.sleep(2)
    print("Initial Results:")
    print(get_search_results_list(max_results=3))
    
    # 3. Filter: Sort by Most Likes (最多点赞)
    print("\n[3] Filter: Sort by Most Likes (最多点赞)...")
    print(filter_results("排序依据", "最多点赞"))
    time.sleep(3)
    print("Results after 'Most Likes':")
    print(get_search_results_list(max_results=3))

    # 4. Filter: Type = Video (视频)
    print("\n[4] Filter: Type = Video (视频)...")
    print(filter_results("笔记类型", "视频"))
    time.sleep(3)
    print("Results after 'Video':")
    print(get_search_results_list(max_results=3))

    # 5. Filter: Location = Nearby (附近)
    print("\n[5] Filter: Location = Nearby (附近) - DIRECT ACTION...")
    # Using direct action instead of MCP wrapper as requested
    apply_search_filters(state.page, {"位置距离": "附近"})
    time.sleep(3)
    print("Results after 'Nearby':")
    print(get_search_results_list(max_results=3))
    
    # 6. Filter: Time = One Day (一天内)
    print("\n[6] Filter: Time = One Day (一天内)...")
    print(filter_results("发布时间", "一天内"))
    time.sleep(3)
    print("Results after 'One Day':")
    print(get_search_results_list(max_results=3))

    # 7. Filter: Search Scope = Not Viewed (未看过)
    print("\n[7] Filter: Search Scope = Not Viewed (未看过)...")
    print(filter_results("搜索范围", "未看过"))
    time.sleep(3)
    print("Results after 'Not Viewed':")
    print(get_search_results_list(max_results=3))

    print("\n--- Test Complete ---")
    
    input("Press Enter to close browser...")

    # Cleanup
    if state.context:
        state.context.close()
    if state.playwright:
        state.playwright.stop()

if __name__ == "__main__":
    test_mcp_tools()
