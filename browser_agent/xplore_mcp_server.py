import sys
import os
from typing import Optional
from mcp.server.fastmcp import FastMCP
from playwright.sync_api import sync_playwright, Page, BrowserContext

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_browser_utils import launch_user_browser
from xplore_actions import (
    search_xplore, 
    document_download_xplore, 
    search_extract_xplore, 
    navigate_to_page_xplore, 
    document_page_xplore
)
from config import settings as config

# Initialize FastMCP server
mcp = FastMCP("IEEE Xplore Browser Agent")

# Global state for browser
class BrowserState:
    playwright = None
    context: Optional[BrowserContext] = None
    page: Optional[Page] = None

state = BrowserState()

@mcp.tool()
def launch_browser() -> str:
    """
    Connects to the persistent user browser session for IEEE Xplore.
    Must be called before any other tools.
    """
    if state.page:
        return "Browser is already connected."
    
    try:
        state.playwright = sync_playwright().start()
        state.context, state.page = launch_user_browser(state.playwright)
        
        # Navigate to IEEE Xplore home to ensure we are ready
        state.page.goto("https://ieeexplore.ieee.org/Xplore/home.jsp")
        return "Browser connected successfully and navigated to IEEE Xplore."
    except Exception as e:
        return f"Failed to connect to browser: {str(e)}"

@mcp.tool()
def search(query: str) -> str:
    """
    Searches for a keyword on IEEE Xplore.
    
    Args:
        query: The search term (e.g., "Deep Learning", "Robotics").
    """
    if not state.page:
        return "Error: Browser not connected. Call launch_browser() first."
    
    try:
        search_xplore(state.page, query)
        return f"Search for '{query}' completed."
    except Exception as e:
        return f"Search failed: {str(e)}"

@mcp.tool()
def get_search_results(start_index: int = 1, end_index: int = 10) -> str:
    """
    Extracts the list of papers from the current search results page.
    
    Args:
        start_index: The rank of the first paper to extract (1-based).
        end_index: The rank of the last paper to extract (1-based).
    """
    if not state.page:
        return "Error: Browser not connected. Call launch_browser() first."
    
    try:
        return search_extract_xplore(state.page, start_index, end_index)
    except Exception as e:
        return f"Extraction failed: {str(e)}"

@mcp.tool()
def go_to_page(page_number: int) -> str:
    """
    Navigates to a specific page of search results.
    
    Args:
        page_number: The page number to navigate to (1-based).
    """
    if not state.page:
        return "Error: Browser not connected. Call launch_browser() first."
    
    try:
        return navigate_to_page_xplore(state.page, page_number)
    except Exception as e:
        return f"Navigation failed: {str(e)}"

@mcp.tool()
def open_document(result_index: int) -> str:
    """
    Opens a specific paper from the search results in a new tab and extracts its details.
    Updates the browser state to focus on this new tab.
    
    Args:
        result_index: The 1-based index of the paper in the search results list.
    """
    if not state.page:
        return "Error: Browser not connected. Call launch_browser() first."
    
    try:
        new_page, info = document_page_xplore(state.page, result_index)
        # Update global state to track the new page
        state.page = new_page
        return f"Opened document in new tab.\n\n{info}"
    except Exception as e:
        return f"Failed to open document: {str(e)}"

@mcp.tool()
def download_current_paper() -> str:
    """
    Attempts to download the PDF of the paper currently displayed on the page.
    The page must be an article detail page or have a visible PDF button.
    """
    if not state.page:
        return "Error: Browser not connected. Call launch_browser() first."
    
    try:
        result = document_download_xplore(state.page)
        return result
    except Exception as e:
        return f"Download failed: {str(e)}"

@mcp.tool()
def list_tabs() -> str:
    """
    Lists all open tabs with their titles and URLs.
    Returns a formatted string where the active tab is marked with *.
    """
    if not state.context:
        return "Error: Browser not connected. Call launch_browser() first."
    
    try:
        pages = state.context.pages
        info = []
        for i, p in enumerate(pages):
            active_marker = "*" if p == state.page else " "
            info.append(f"{active_marker} [{i}] {p.title()} ({p.url})")
        return "\n".join(info)
    except Exception as e:
        return f"Failed to list tabs: {str(e)}"

@mcp.tool()
def switch_tab(index: int) -> str:
    """
    Switches focus to a specific tab index.
    
    Args:
        index: The 0-based index of the tab to switch to.
    """
    if not state.context:
        return "Error: Browser not connected. Call launch_browser() first."
    
    try:
        pages = state.context.pages
        if 0 <= index < len(pages):
            state.page = pages[index]
            state.page.bring_to_front()
            return f"Switched to tab {index}: {state.page.title()}"
        else:
            return f"Error: Invalid tab index {index}. Max index is {len(pages)-1}."
    except Exception as e:
        return f"Failed to switch tab: {str(e)}"

@mcp.tool()
def close_tab(index: int) -> str:
    """
    Closes a specific tab index.
    
    Args:
        index: The 0-based index of the tab to close.
    """
    if not state.context:
        return "Error: Browser not connected. Call launch_browser() first."
    
    try:
        pages = state.context.pages
        if 0 <= index < len(pages):
            page_to_close = pages[index]
            title = page_to_close.title()
            page_to_close.close()
            
            # Update state.page if we closed the active one
            if page_to_close == state.page:
                # Try to switch to the last available tab
                if state.context.pages:
                    state.page = state.context.pages[-1]
                    state.page.bring_to_front()
                else:
                    state.page = None
            
            return f"Closed tab {index}: {title}"
        else:
            return f"Error: Invalid tab index {index}."
    except Exception as e:
        return f"Failed to close tab: {str(e)}"

if __name__ == "__main__":
    mcp.run()
