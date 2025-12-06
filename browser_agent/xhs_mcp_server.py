import sys
import os
from typing import Optional
from mcp.server.fastmcp import FastMCP
from playwright.sync_api import sync_playwright, Page, BrowserContext

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from browser_utils import launch_persistent_browser
from xhs_actions import search_xhs, extract_search_results, extract_post_details, close_post_details, apply_search_filters
from config import settings as config

# Initialize FastMCP server
# This server exposes the browser automation tools to any MCP-compatible client (e.g., Claude Desktop, Cursor).
mcp = FastMCP("XHS Browser Agent")

# Global state for browser
# We use a global state to maintain the browser session across multiple tool calls.
class BrowserState:
    playwright = None
    context: Optional[BrowserContext] = None
    page: Optional[Page] = None

state = BrowserState()

@mcp.tool()
def launch_browser() -> str:
    """
    Launches the persistent browser session for Xiaohongshu.
    Must be called before any other tools.
    
    This tool initializes the Playwright browser with:
    1. Persistent context (saves cookies/login).
    2. Stealth settings (evades bot detection).
    3. Auto-detected geolocation (enables 'Nearby' features).
    """
    if state.page:
        return "Browser is already running."
    
    try:
        state.playwright = sync_playwright().start()
        state.context, state.page = launch_persistent_browser(state.playwright)
        
        # Navigate to home to ensure we are ready
        state.page.goto(config.XHS_EXPLORE_URL)
        return "Browser launched successfully and navigated to XHS Explore page."
    except Exception as e:
        return f"Failed to launch browser: {str(e)}"

@mcp.tool()
def search(query: str) -> str:
    """
    Searches for a keyword on Xiaohongshu.
    
    Args:
        query: The search term (e.g., "AI Agent", "Python tutorial").
    """
    if not state.page:
        return "Error: Browser not running. Call launch_browser() first."
    
    try:
        search_xhs(state.page, query)
        return f"Search for '{query}' completed."
    except Exception as e:
        return f"Search failed: {str(e)}"

@mcp.tool()
def filter_results(category: str, option: str) -> str:
    """
    Applies a search filter. You must use the EXACT option names listed below.
    
    Args:
        category: Filter category. Allowed values: "排序依据", "笔记类型", "发布时间", "搜索范围", "位置距离"
        option: Filter option. You MUST use one of the following EXACT strings:
            - For "排序依据": "综合", "最新", "最多点赞", "最多评论", "最多收藏"
            - For "笔记类型": "不限", "视频", "图文"
            - For "发布时间": "不限", "一天内", "一周内", "半年内"
            - For "搜索范围": "不限", "已看过", "未看过", "已关注"
            - For "位置距离": "不限", "同城", "附近"
    """
    if not state.page:
        return "Error: Browser not running. Call launch_browser() first."
    
    try:
        apply_search_filters(state.page, {category: option})
        return f"Applied filter: {category} = {option}"
    except Exception as e:
        return f"Filter application failed: {str(e)}"

@mcp.tool()
def get_search_results_list(max_results: int = 10) -> str:
    """
    Extracts the list of search results (titles and likes) from the current page.
    Returns a Markdown table string.
    """
    if not state.page:
        return "Error: Browser not running. Call launch_browser() first."
    
    try:
        return extract_search_results(state.page, max_results)
    except Exception as e:
        return f"Extraction failed: {str(e)}"

@mcp.tool()
def open_post(index: int) -> str:
    """
    Opens a specific post from the search results by index (0-based).
    
    Args:
        index: The index of the post to open (e.g., 0 for the first post).
    """
    if not state.page:
        return "Error: Browser not running. Call launch_browser() first."
    
    try:
        # The cover is the clickable image area defined by class "cover"
        covers = state.page.locator(".cover").all()
        if index >= len(covers):
            return f"Error: Index {index} out of range. Only {len(covers)} posts found."
            
        target_cover = covers[index]
        target_cover.wait_for(state="visible", timeout=5000)
        target_cover.click()
        
        # Wait for modal
        state.page.wait_for_selector("#noteContainer", timeout=10000)
        return f"Opened post at index {index}."
    except Exception as e:
        return f"Failed to open post: {str(e)}"

@mcp.tool()
def get_post_details() -> str:
    """
    Extracts full details from the currently open post modal.
    Includes text, tags, stats, and comments.
    """
    if not state.page:
        return "Error: Browser not running. Call launch_browser() first."
    
    try:
        return extract_post_details(state.page)
    except Exception as e:
        return f"Detail extraction failed: {str(e)}"

@mcp.tool()
def close_post() -> str:
    """
    Closes the currently open post modal.
    """
    if not state.page:
        return "Error: Browser not running. Call launch_browser() first."
    
    try:
        close_post_details(state.page)
        return "Post closed."
    except Exception as e:
        return f"Failed to close post: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
