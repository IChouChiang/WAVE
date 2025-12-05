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

def navigate_to_page_xplore(page: Page, page_number: int) -> str:
    """
    Navigates to a specified page in IEEE Xplore search results.
    
    Basic functionality:
    1. If the page number is valid and exists, navigate to that page and return success message
    2. If the page number is invalid (e.g., 0 or negative), navigate to page 1 and return reminder message
    3. If the page does not exist (out of bounds), navigate to page 1 and return reminder message
    
    Note: This function only handles navigation, not page information extraction. Use search_extract_xplore function for extraction.
    
    Args:
        page (Page): Playwright page object
        page_number (int): Page number to navigate to (1‑based)
        
    Returns:
        str: Navigation result message string
    """
    try:
        # Check if on search results page
        current_url = page.url
        if "search/searchresult.jsp" not in current_url:
            return "Error: Not on search results page"
        
        # Save original page number for message
        original_page = page_number
        
        # Handle invalid page numbers (0 or negative)
        if page_number < 1:
            page_number = 1
        
        # Modify page number parameter in URL
        import re
        
        if "pageNumber=" in current_url:
            new_url = re.sub(r'pageNumber=\d+', f'pageNumber={page_number}', current_url)
        else:
            if "?" in current_url:
                new_url = current_url + f"&pageNumber={page_number}"
            else:
                new_url = current_url + f"?pageNumber={page_number}"
        
        # Navigate to new URL
        page.goto(new_url)
        
        # Wait for page load
        try:
            page.wait_for_load_state("domcontentloaded", timeout=15000)
        except:
            pass  # Continue even if timeout
        
        time.sleep(2)
        
        # Check for 'no results' message (page out of bounds)
        try:
            no_results_selector = "#xplMainContent > div.ng-SearchResults.row.g-0 > div.col > xpl-results-list > div > div > p.List-results-none--lg.u-mb-0"
            no_results_element = page.locator(no_results_selector).first
            if no_results_element.is_visible():
                no_results_text = no_results_element.inner_text().strip()
                if "We were unable to find results for" in no_results_text:
                    # Page out of bounds, navigate back to page 1
                    if "pageNumber=" in page.url:
                        page1_url = re.sub(r'pageNumber=\d+', 'pageNumber=1', page.url)
                    else:
                        page1_url = page.url + ("&pageNumber=1" if "?" in page.url else "?pageNumber=1")
                    
                    page.goto(page1_url)
                    
                    try:
                        page.wait_for_load_state("domcontentloaded", timeout=15000)
                    except:
                        pass
                    
                    time.sleep(2)
                    
                    if original_page < 1:
                        return f"Note: Page number {original_page} is invalid, navigated to page 1"
                    else:
                        return f"Note: Page {original_page} does not exist (out of bounds), navigated to page 1"
        except:
            pass  # No 'no results' message
        
        # Normal case: return success message
        if original_page < 1:
            return f"Note: Page number {original_page} is invalid, navigated to page 1"
        else:
            return f"Successfully navigated to page {page_number}"
        
    except Exception as e:
        return f"Error navigating to page {page_number}: {e}"

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
            # Try to parse total_results as integer (remove commas)
            try:
                total_int = int(total_results.replace(',', ''))
                # Each page shows up to 25 results
                total_pages = (total_int + 24) // 25  # ceil division
                
                # Detect current page from pagination UI
                current_page = 1  # default
                try:
                    # Look for active pagination button with class containing "active"
                    pagination_selector = "#xplMainContent > div.ng-SearchResults.row.g-0 > div.col > xpl-paginator > div.pagination-bar.hide-mobile.text-base-md-lh > ul"
                    pagination_list = page.locator(pagination_selector).first
                    if pagination_list.is_visible():
                        # Find the active button
                        active_button = pagination_list.locator("button.active").first
                        if active_button.is_visible():
                            page_text = active_button.inner_text().strip()
                            if page_text.isdigit():
                                current_page = int(page_text)
                                print(f"Detected current page from pagination: {current_page}")
                except:
                    pass  # Keep default page 1 if detection fails
                
                if search_keywords:
                    output_lines.append(f"Showing {result_range} of {total_results} results for {search_keywords}")
                    output_lines.append(f"Page {current_page} of {total_pages} (up to 25 results per page)")
                else:
                    output_lines.append(f"Showing {result_range} of {total_results} results")
                    output_lines.append(f"Page {current_page} of {total_pages} (up to 25 results per page)")
            except ValueError:
                # If we can't parse total_results as integer, fall back to simple output
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

def document_page_xplore(page: Page, result_index: int = 1):
    """
    Opens an IEEE Xplore document page in a new tab by clicking on a result link.
    
    Args:
        page (Page): The Playwright page object.
        result_index (int): The 1-based index of the result to open. Default is 1 (first result).
        
    Returns:
        tuple: (new_page, document_url) where new_page is the Page object for the new tab,
               and document_url is the URL of the opened document.
               
    Behavior:
        1. Finds the result item at the specified index.
        2. Clicks the document link (opens in new tab).
        3. Waits for the new tab to load.
        4. Returns the new page and document URL.
    """
    print(f"Opening document at result index {result_index} in new tab...")
    
    try:
        # Wait for results to load
        page.wait_for_selector("#xplMainContent", timeout=10000)
        time.sleep(1)
        
        # Find all result items
        result_items = page.locator("#xplMainContent > div.ng-SearchResults.row.g-0 > div.col > xpl-results-list xpl-results-item").all()
        
        if not result_items:
            raise ValueError("No result items found on the page")
        
        # Validate index
        if result_index < 1 or result_index > len(result_items):
            raise ValueError(f"Result index {result_index} out of range. Available results: {len(result_items)}")
        
        # Get the target result item (0-based index)
        target_item = result_items[result_index - 1]
        
        # Find the document link within the result item
        # Using the selector pattern: #\31 0036606 > xpl-results-item > div.hide-mobile > div.d-flex.result-item > div.col.result-item-align.px-3 > h3 > a
        # But we need a more generic approach
        document_link = target_item.locator("h3 a.fw-bold").first
        
        if not document_link.is_visible():
            raise ValueError(f"Document link not visible for result index {result_index}")
        
        # Get the href attribute before clicking
        document_url = document_link.get_attribute("href")
        if not document_url:
            raise ValueError("Could not get document URL from link")
        
        # Ensure we have the full URL
        if document_url.startswith("/"):
            document_url = f"https://ieeexplore.ieee.org{document_url}"
        
        print(f"Document URL: {document_url}")
        
        # Create a new tab programmatically instead of clicking with modifier
        # This is more reliable than Control+click
        print("Creating new tab...")
        
        # Create a new page in the same context
        new_page = page.context.new_page()
        
        # Navigate to the document URL
        print(f"Navigating to document URL in new tab...")
        new_page.goto(document_url)
        
        # Wait for the new page to load with shorter timeout
        try:
            new_page.wait_for_load_state("domcontentloaded", timeout=15000)
        except:
            print("Warning: Timeout waiting for domcontentloaded, continuing anyway")
        
        time.sleep(2)
        
        print(f"Successfully opened document in new tab: {new_page.url}")
        
        # Verify we have both tabs
        print(f"Total tabs in context: {len(page.context.pages)}")
        
        # Extract document information for LLM-friendly output (inline)
        print("Extracting document information in new tab...")
        output_lines = []
        try:
            # Extract document title
            title = ""
            try:
                title_selector = "#xplMainContentLandmark > div > xpl-document-details > div > div.document-main.global-content-width-w-rr > section.document-main-header.row.g-0 > div > xpl-document-header > section > div.document-header-inner-container.row.g-0 > div.document-header-content.col-10 > div > div.row.g-0.document-title-fix > div > div.left-container.w-100 > h1 > span"
                title_element = new_page.locator(title_selector).first
                if title_element.is_visible(timeout=5000):
                    title = title_element.inner_text().strip()
                    print(f"Found title using specific selector: {title[:100]}...")
            except:
                pass

            if not title:
                try:
                    title_element = new_page.locator("h1.document-title").first
                    if title_element.is_visible(timeout=3000):
                        title = title_element.inner_text().strip()
                        print(f"Found title using h1.document-title: {title[:100]}...")
                except:
                    pass

            if not title:
                try:
                    title_element = new_page.locator("h1").first
                    if title_element.is_visible(timeout=3000):
                        title = title_element.inner_text().strip()
                        print(f"Found title using h1: {title[:100]}...")
                except:
                    pass

            # Extract abstract
            abstract = ""
            try:
                abstract_selector = "#xplMainContentLandmark > div > xpl-document-details > div > div.document-main.global-content-width-w-rr > div > div.document-main-content-container.col-19-24 > section > div.document-main-left-trail-content > div > xpl-document-abstract > section > div.abstract-desktop-div.hide-mobile.text-base-md-lh > div.abstract-text.row.g-0 > div > div > h2"
                abstract_element = new_page.locator(abstract_selector).first
                if abstract_element.is_visible(timeout=5000):
                    abstract_container = abstract_element.locator("xpath=..").locator("div[xplmathjax]").first
                    if abstract_container.is_visible(timeout=3000):
                        abstract = abstract_container.inner_text().strip()
                        print(f"Found abstract using specific selector: {abstract[:100]}...")
            except:
                pass

            if not abstract:
                try:
                    abstract_element = new_page.locator("#abstract").first
                    if abstract_element.is_visible(timeout=3000):
                        abstract = abstract_element.inner_text().strip()
                        print(f"Found abstract using #abstract: {abstract[:100]}...")
                except:
                    pass

            if not abstract:
                try:
                    abstract_element = new_page.locator("[class*='abstract']").first
                    if abstract_element.is_visible(timeout=3000):
                        abstract = abstract_element.inner_text().strip()
                        print(f"Found abstract using class*='abstract': {abstract[:100]}...")
                except:
                    pass

            # Keep full abstract (no truncation) — embeddings/LLM downstream will manage size
            short_abstract = abstract

            # Compose output
            output_lines.append("=" * 80)
            output_lines.append("DOCUMENT INFORMATION")
            output_lines.append("=" * 80)
            if title:
                output_lines.append(f"\n**Title:** {title}")
            else:
                output_lines.append(f"\n**Title:** Not found")

            if short_abstract:
                output_lines.append(f"\n**Abstract:** {short_abstract}")
            else:
                output_lines.append(f"\n**Abstract:** Not found")

            # URL
            output_lines.append(f"\n**URL:** {new_page.url}")

            document_info = "\n".join(output_lines)
        except Exception as e:
            document_info = f"Error extracting document information: {e}"

        return new_page, document_info
        
    except Exception as e:
        print(f"Error opening document: {e}")
        raise

# Note: extract_document_info inlined into document_page_xplore; separate function removed.