"""
IEEE Xplore actions for academic paper collection.
Simple functions for interacting with IEEE Xplore website.
"""

import time
from playwright.sync_api import Page

def search_xplore(page: Page, query: str):
    """
    Performs a search on IEEE Xplore website.
    
    Args:
        page (Page): The Playwright page object.
        query (str): The search keyword.
        
    Behavior:
        1. Locates the search input box using get_by_role method.
        2. Fills the input with the search query.
        3. Clicks the search button to submit the search.
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
    
    # Click the search button - need to be specific about which "Search" button
    print("Clicking search button...")
    
    # There are multiple buttons with "Search" in the name on results page
    # We need the main search button with aria-label="Search" (not "Search Within")
    # Use exact match for the name
    search_button = page.get_by_role("button", name="Search", exact=True)
    
    # Wait for the button to be visible
    search_button.wait_for(state="visible", timeout=5000)
    
    # Click the search button
    search_button.click()
    
    # Wait for search to complete
    time.sleep(3)
    print("Search submitted successfully")