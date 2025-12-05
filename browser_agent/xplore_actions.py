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

def search_extract_xplore(page: Page, start_index: int = 1, end_index: int = 10) -> str:
    """
    Extracts search results information from IEEE Xplore search results page.
    
    Args:
        page (Page): The Playwright page object.
        start_index (int): Starting index of results to extract (1-based). Default is 1.
        end_index (int): Ending index of results to extract (1-based). Default is 10.
                            
    Returns:
        str: A formatted string with summary and selected paper details.
             Example: extracts results 3, 4, 5 when start_index=3, end_index=5
    """
    output_lines = []
    
    try:
        # Validate parameters
        if start_index < 1:
            return "start_index must be greater than 0"
        if end_index < start_index:
            return "end_index must be greater than or equal to start_index"
        
        # Calculate range size and limit to max 10 results
        range_size = end_index - start_index + 1
        if range_size > 10:
            end_index = start_index + 9  # Limit to 10 results max
            print(f"Range limited to {start_index}-{end_index} (max 10 results)")
        
        # Wait for search results to load
        page.wait_for_selector("#xplMainContent", timeout=10000)
        time.sleep(1)
        
        # Extract summary information
        result_range = ""
        total_results = ""
        search_keywords = ""
        
        try:
            range_selector = "#xplMainContent > div.ng-Dashboard > div.col > xpl-search-dashboard > section > div > h1 > span:nth-child(1) > span:nth-child(1)"
            range_element = page.locator(range_selector).first
            if range_element.is_visible():
                result_range = range_element.inner_text().strip()
        except:
            pass
        
        try:
            total_selector = "#xplMainContent > div.ng-Dashboard > div.col > xpl-search-dashboard > section > div > h1 > span:nth-child(1) > span:nth-child(2)"
            total_element = page.locator(total_selector).first
            if total_element.is_visible():
                total_results = total_element.inner_text().strip()
        except:
            pass
        
        try:
            keywords_selector = "#xplMainContent > div.ng-Dashboard > div.col > xpl-search-dashboard > section > div > h1 > span:nth-child(2) > strong > xpl-breadcrumb > div > span > span > span > span"
            keywords_element = page.locator(keywords_selector).first
            if keywords_element.is_visible():
                search_keywords = keywords_element.inner_text().strip()
        except:
            pass
        
        # Add summary to output
        if result_range and total_results:
            if search_keywords:
                output_lines.append(f"Showing {result_range} of {total_results} results for {search_keywords}")
            else:
                output_lines.append(f"Showing {result_range} of {total_results} results")
        else:
            output_lines.append("No search results information found")
        
        # Extract detailed paper information for the specified range
        output_lines.append(f"\n### Papers {start_index}-{end_index}:")
        
        try:
            # Find all result items in the results list
            result_items = page.locator("#xplMainContent > div.ng-SearchResults.row.g-0 > div.col > xpl-results-list xpl-results-item").all()
            
            if result_items:
                total_items = len(result_items)
                output_lines.append(f"Found {total_items} papers on this page")
                
                # Convert to 0-based indices
                start_idx = start_index - 1
                end_idx = end_index - 1
                
                # Validate indices
                if start_idx >= total_items:
                    output_lines.append(f"Start index {start_index} exceeds available results ({total_items})")
                else:
                    # Adjust end index if it exceeds available results
                    end_idx = min(end_idx, total_items - 1)
                    
                    # Extract papers in the specified range
                    for i in range(start_idx, end_idx + 1):
                        try:
                            item = result_items[i]
                            
                            # Extract title
                            title = ""
                            try:
                                title_elem = item.locator("h3 a.fw-bold").first
                                if title_elem.is_visible():
                                    title = title_elem.inner_text().strip()
                            except:
                                pass
                            
                            # Extract authors
                            authors = ""
                            try:
                                author_elems = item.locator("xpl-authors-name-list .author a span").all()
                                if author_elems:
                                    author_names = [elem.inner_text().strip() for elem in author_elems if elem.is_visible()]
                                    authors = "; ".join(author_names)
                            except:
                                pass
                            
                            # Extract source/conference
                            source = ""
                            try:
                                source_elem = item.locator(".description a").first
                                if source_elem.is_visible():
                                    source = source_elem.inner_text().strip()
                            except:
                                pass
                            
                            # Extract metadata (year, type, publisher)
                            metadata_parts = []
                            try:
                                # Get all metadata spans in the publisher-info-container
                                try:
                                    metadata_spans = item.locator(".publisher-info-container span").all()
                                    
                                    for span in metadata_spans:
                                        if span.is_visible():
                                            text = span.inner_text().strip()
                                            # Skip separator-only text (just "|" or similar)
                                            if text and text != "|":
                                                # Clean the text: remove leading "| " if present
                                                if text.startswith("| "):
                                                    text = text[2:].strip()
                                                
                                                # Check if this is a document type (based on IEEE Xplore actual types)
                                                doc_types = [
                                                    "Conference Paper", "Journal Article", "Book",
                                                    "Magazine", "Early Access Article", "Standard", 
                                                    "Course", "Early Access"
                                                ]
                                                
                                                is_doc_type = any(doc_type in text for doc_type in doc_types)
                                                is_year = text.startswith("Year:")
                                                is_publisher = "Publisher:" in text or text in ["IEEE", "Springer", "ACM", "Wiley"]
                                                
                                                # Add if it's year, document type, or publisher
                                                if is_year or is_doc_type or is_publisher:
                                                    # Skip partial publisher entries like just "Publisher:"
                                                    if text == "Publisher:":
                                                        continue
                                                    
                                                    # Avoid duplicates
                                                    clean_text = text.replace("Publisher: ", "")
                                                    if not any(clean_text in part.replace("Publisher: ", "") for part in metadata_parts):
                                                        metadata_parts.append(text)
                                except:
                                    pass
                                
                                # If we didn't find publisher in spans, try xpl-publisher element
                                if not any("Publisher:" in part or part in ["IEEE", "Springer", "ACM", "Wiley"] for part in metadata_parts):
                                    try:
                                        publisher_elem = item.locator("xpl-publisher").first
                                        if publisher_elem.is_visible():
                                            publisher_text = publisher_elem.inner_text().strip()
                                            if publisher_text:
                                                # Clean up publisher text
                                                if "Publisher:" not in publisher_text:
                                                    publisher_text = f"Publisher: {publisher_text}"
                                                metadata_parts.append(publisher_text)
                                    except:
                                        pass
                                
                                # Combine all metadata parts
                                if metadata_parts:
                                    metadata = " | ".join(metadata_parts)
                                else:
                                    metadata = ""
                                    
                            except:
                                metadata = ""
                            
                            # Format the paper information
                            paper_num = i + 1
                            output_lines.append(f"\n**{paper_num}. {title}**")
                            if authors:
                                output_lines.append(f"   Authors: {authors}")
                            if source:
                                output_lines.append(f"   Source: {source}")
                            if metadata:
                                output_lines.append(f"   Info: {metadata}")
                            
                        except Exception as e:
                            paper_num = i + 1
                            output_lines.append(f"\n**{paper_num}. Error extracting paper: {str(e)[:50]}...**")
                            continue
                    
                    # Show if there are more papers beyond the extracted range
                    if end_idx < total_items - 1:
                        remaining = total_items - (end_idx + 1)
                        output_lines.append(f"\n... and {remaining} more papers")
            else:
                output_lines.append("No paper results found")
                
        except Exception as e:
            output_lines.append(f"\nError extracting paper details: {e}")
        
        return "\n".join(output_lines)
        
    except Exception as e:
        return f"Error extracting search results: {e}"