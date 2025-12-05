"""
IEEE Xplore actions for academic paper collection.
Simple functions for interacting with IEEE Xplore website.
"""

import time
from playwright.sync_api import Page

def search_xplore(page: Page, query: str, submit_search: bool = False):
    """
    Performs a search on IEEE Xplore website.
    
    Args:
        page (Page): The Playwright page object.
        query (str): The search keyword.
        submit_search (bool): Whether to press Enter to submit the search. Default is False.
        
    Behavior:
        1. Locates the search input box using get_by_role method.
        2. Fills the input with the search query.
        3. Optionally presses 'Enter' to submit the search.
    """
    print(f"Searching IEEE Xplore for: {query}")
    
    # Use get_by_role to locate the search input
    search_input = page.get_by_role("searchbox", name="main")
    
    # Wait for the search input to be visible
    search_input.wait_for(state="visible", timeout=10000)
    
    # Click to focus on the input
    search_input.click()
    time.sleep(0.5)  # Wait for focus
    
    # Fill the input with the search query
    search_input.fill(query)
    
    # Optionally submit search by pressing Enter
    if submit_search:
        search_input.press("Enter")
        time.sleep(2)  # Wait for search to complete