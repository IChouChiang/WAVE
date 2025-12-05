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

def search_extract_xplore(page: Page) -> str:
    """
    Extracts search results information from IEEE Xplore search results page.
    
    Args:
        page (Page): The Playwright page object.
        
    Returns:
        str: A formatted string like: "Showing 1-25 of 26 results for opf NN"
    """
    try:
        # Wait for search results to load
        page.wait_for_selector("#xplMainContent", timeout=10000)
        time.sleep(1)
        
        # Extract result range (e.g., "1-25")
        result_range = ""
        try:
            range_selector = "#xplMainContent > div.ng-Dashboard > div.col > xpl-search-dashboard > section > div > h1 > span:nth-child(1) > span:nth-child(1)"
            range_element = page.locator(range_selector).first
            if range_element.is_visible():
                result_range = range_element.inner_text().strip()
        except:
            pass
        
        # Extract total results (e.g., "26")
        total_results = ""
        try:
            total_selector = "#xplMainContent > div.ng-Dashboard > div.col > xpl-search-dashboard > section > div > h1 > span:nth-child(1) > span:nth-child(2)"
            total_element = page.locator(total_selector).first
            if total_element.is_visible():
                total_results = total_element.inner_text().strip()
        except:
            pass
        
        # Extract search keywords (e.g., "opf NN")
        search_keywords = ""
        try:
            keywords_selector = "#xplMainContent > div.ng-Dashboard > div.col > xpl-search-dashboard > section > div > h1 > span:nth-child(2) > strong > xpl-breadcrumb > div > span > span > span > span"
            keywords_element = page.locator(keywords_selector).first
            if keywords_element.is_visible():
                search_keywords = keywords_element.inner_text().strip()
        except:
            pass
        
        # Format the output
        if result_range and total_results:
            if search_keywords:
                return f"Showing {result_range} of {total_results} results for {search_keywords}"
            else:
                return f"Showing {result_range} of {total_results} results"
        else:
            return "No search results information found"
        
    except Exception as e:
        return f"Error extracting search results: {e}"