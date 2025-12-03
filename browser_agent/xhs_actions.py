import time
from playwright.sync_api import Page

def search_xhs(page: Page, query: str):
    """
    Performs a search on Xiaohongshu (Little Red Book).
    
    Args:
        page (Page): The Playwright page object.
        query (str): The search keyword.
        
    Behavior:
        1. Checks if there's existing text in the search bar (looks for the 'x' close icon).
        2. Clears it if found.
        3. Types the new query.
        4. Presses 'Enter' to submit (more robust than clicking the search button).
        5. Waits for the results to load (checks for .footer element).
    """
    print(f"Searching for: {query}")
    
    # 1. Check for close icon (clear button) and click if it exists
    try:
        close_icon = page.locator(".input-box .close-icon")
        if close_icon.is_visible(timeout=1000):
            print("Clearing existing text...")
            close_icon.click()
            time.sleep(0.5) # Short wait for UI update
    except Exception:
        pass
    
    # 2. Type the query
    search_input = page.locator("#search-input")
    search_input.click()
    search_input.fill(query)
    print(f"Typed: {query}")
    
    # 3. Submit search (Press Enter)
    search_input.press("Enter")
    print("Pressed Enter to search")
    
    # Wait for results to load
    time.sleep(2) 
    try:
        page.wait_for_selector(".footer", timeout=10000)
        print("Search results loaded (found .footer)")
    except:
        print("Warning: Timeout waiting for results")

def apply_search_filters(page: Page, filters: dict):
    """
    Applies search filters by interacting with the filter dropdown.
    
    Args:
        page (Page): The Playwright page object.
        filters (dict): A dictionary of filters to apply.
                        Key: Category name. Supported categories and options:
                             - "排序依据": "综合", "最新", "最多点赞", "最多评论", "最多收藏"
                             - "笔记类型": "不限", "视频", "图文"
                             - "发布时间": "不限", "一天内", "一周内", "半年内"
                             - "搜索范围": "不限", "已看过", "未看过", "已关注"
                             - "位置距离": "不限", "同城", "附近"
                        Value: Option name (e.g., "最新", "视频", "未看过")
    """
    print(f"Applying filters: {filters}")
    
    # Selector for the filter dropdown button
    filter_btn_selector = ".search-layout__top clientonly > div > span"
    
    for category, option in filters.items():
        print(f"Setting '{category}' to '{option}'...")
        
        try:
            # 1. Open the dropdown if not visible
            if not page.locator(".filters-wrapper").is_visible():
                print("Opening filter dropdown...")
                # Try to find the button. If the specific selector fails, try a broader one or handle error.
                btn = page.locator(filter_btn_selector)
                if not btn.is_visible():
                     # Fallback: sometimes the structure might be slightly different or it's just ".filter-box"
                     # But based on user input, we stick to the structure.
                     pass
                btn.click()
                page.wait_for_selector(".filters-wrapper", timeout=3000)
            
            # 2. Find the category row
            filter_rows = page.locator(".filters-wrapper .filters").all()
            target_row = None
            
            for row in filter_rows:
                # The first span in the row is usually the category title
                cat_span = row.locator("span").first
                if cat_span.is_visible() and category in cat_span.inner_text():
                    target_row = row
                    break
            
            if not target_row:
                print(f"Category '{category}' not found.")
                continue
                
            # 3. Find and click the option
            option_clicked = False
            tags = target_row.locator(".tags").all()
            for tag in tags:
                if tag.inner_text().strip() == option:
                    # Check if already active
                    class_attr = tag.get_attribute("class") or ""
                    if "active" in class_attr:
                        print(f"Option '{option}' is already active.")
                        option_clicked = True
                    else:
                        tag.click()
                        print(f"Clicked option '{option}'.")
                        option_clicked = True
                        # Wait for reload/update. 
                        # Note: Clicking a filter often triggers a reload which might close the dropdown.
                        time.sleep(2) 
                    break
            
            if not option_clicked:
                print(f"Option '{option}' not found in category '{category}'.")
                
        except Exception as e:
            print(f"Error applying filter {category}={option}: {e}")

def extract_search_results(page: Page, max_results: int = 15) -> str:
    """
    Extracts the top N search results (Title and Likes) and returns a Markdown table string.
    
    Args:
        page (Page): The Playwright page object.
        max_results (int): Maximum number of results to extract (default: 15).
        
    Returns:
        str: A Markdown formatted table of results.
    """
    output = []
    output.append(f"\n### Top {max_results} Results for current search")
    output.append("| Title | Likes |")
    output.append("| --- | --- |")
    
    try:
        page.wait_for_selector(".footer", timeout=5000)
    except:
        return "No results found."

    footers = page.locator(".footer").all()
    
    count = 0
    for footer in footers:
        if count >= max_results:
            break
            
        try:
            # Extract title
            title_el = footer.locator(".title span").first
            title = title_el.inner_text() if title_el.is_visible() else "No Title"
            
            # Extract likes
            like_el = footer.locator(".like-wrapper .count").first
            likes = like_el.inner_text() if like_el.is_visible() else "0"
            
            # Sanitize title
            title = title.replace("|", "-").replace("\n", " ").strip()
            
            output.append(f"| {title} | {likes} |")
            count += 1
        except Exception as e:
            output.append(f"Error extracting item: {e}")
            continue
    
    result_str = "\n".join(output) + "\n"
    print(result_str) # Keep printing for terminal monitoring
    return result_str

def extract_post_details(page: Page) -> str:
    """
    Extracts detailed information from the currently open post modal.
    
    Args:
        page (Page): The Playwright page object.
        
    Returns:
        str: Structured information in Markdown format.
    """
    output = []
    output.append("\n### Post Details Extraction")
    
    try:
        # Wait for the note container to appear
        page.wait_for_selector("#noteContainer", timeout=10000)
        container = page.locator("#noteContainer")
        
        # 0. Extract Basic Info (Title, Author, Date)
        title = "No Title"
        author = "Unknown"
        date_loc = ""
        
        try:
            # Title
            title_el = container.locator("#detail-title").first
            if title_el.is_visible():
                title = title_el.inner_text().strip()
                
            # Author
            author_el = container.locator(".author-container .username").first
            if author_el.is_visible():
                author = author_el.inner_text().strip()
                
            # Date/Location
            date_el = container.locator(".bottom-container .date").first
            if date_el.is_visible():
                date_loc = date_el.inner_text().strip()
        except Exception as e:
            output.append(f"Error extracting basic info: {e}")
        
        # 1. Extract Text
        note_text = ""
        try:
            # The text content is often split across multiple spans and mixed with images/emojis
            # We need to get the full text content of the .note-text container
            # inner_text() on the container usually concatenates all visible text
            text_container = container.locator("#detail-desc .note-text").first
            if text_container.is_visible():
                note_text = text_container.inner_text().strip()
        except Exception as e:
            output.append(f"Error extracting text: {e}")
            
        # 2. Extract Tags
        tags_list = []
        try:
            tags = container.locator("#hash-tag").all()
            if not tags:
                tags = container.locator("a.tag").all()
            
            for tag in tags:
                if tag.is_visible():
                    text = tag.inner_text().strip()
                    if text.startswith("#"):
                        tags_list.append(text)
        except Exception as e:
            output.append(f"Error extracting tags: {e}")

        # 3. Extract Stats (Likes, Collections, Comments)
        likes = "0"
        collections = "0"
        comments = "0"
        
        try:
            like_el = container.locator(".like-wrapper .count").first
            if like_el.is_visible():
                likes_text = like_el.inner_text().strip()
                likes = "0" if likes_text == "赞" else likes_text
                
            collect_el = container.locator(".collect-wrapper .count").first
            if collect_el.is_visible():
                collect_text = collect_el.inner_text().strip()
                collections = "0" if collect_text == "收藏" else collect_text
                
            chat_el = container.locator(".chat-wrapper .count").first
            if chat_el.is_visible():
                chat_text = chat_el.inner_text().strip()
                comments = "0" if chat_text == "评论" else chat_text
        except Exception as e:
            output.append(f"Error extracting stats: {e}")
            
        # 4. Extract Comments
        comments_list = []
        try:
            comment_count_int = 0
            if comments.isdigit():
                comment_count_int = int(comments)
            
            if comment_count_int > 0:
                output.append("Extracting comments...")
                
                try:
                    container.locator(".parent-comment").first.wait_for(state="visible", timeout=3000)
                except:
                    pass 

                parent_comments = container.locator(".parent-comment").all()[:5]
                
                for i, pc in enumerate(parent_comments):
                    c_data = {}
                    try:
                        c_data['author'] = pc.locator(".author .name").first.inner_text()
                        c_data['content'] = pc.locator(".content .note-text").first.inner_text()
                        
                        date_el = pc.locator(".info .date span").first
                        c_data['date'] = date_el.inner_text() if date_el.is_visible() else ""
                        
                        loc_el = pc.locator(".info .date .location").first
                        c_data['location'] = loc_el.inner_text() if loc_el.is_visible() else ""
                        
                        like_el = pc.locator(".interactions .like .count").first
                        likes_text = like_el.inner_text() if like_el.is_visible() else "0"
                        c_data['likes'] = "0" if likes_text.strip() == "赞" else likes_text
                        
                        top_label = pc.locator(".labels .top").first
                        c_data['is_top'] = top_label.is_visible()
                        
                        c_data['reply'] = None
                        reply_item = pc.locator(".reply-container .comment-item-sub").first
                        if reply_item.is_visible():
                            r_data = {}
                            r_data['author'] = reply_item.locator(".author .name").first.inner_text()
                            r_data['content'] = reply_item.locator(".content .note-text").first.inner_text()
                            
                            r_date_el = reply_item.locator(".info .date span").first
                            r_data['date'] = r_date_el.inner_text() if r_date_el.is_visible() else ""
                            
                            r_loc_el = reply_item.locator(".info .date .location").first
                            r_data['location'] = r_loc_el.inner_text() if r_loc_el.is_visible() else ""
                            
                            r_like_el = reply_item.locator(".interactions .like .count").first
                            r_likes_text = r_like_el.inner_text() if r_like_el.is_visible() else "0"
                            r_data['likes'] = "0" if r_likes_text.strip() == "赞" else r_likes_text
                            
                            c_data['reply'] = r_data
                            
                        comments_list.append(c_data)
                        
                    except Exception as e:
                        output.append(f"Error extracting comment {i}: {e}")
                        
        except Exception as e:
            output.append(f"Error in comment extraction block: {e}")

        # Format as Markdown
        output.append("\n--- Post Analysis ---")
        output.append(f"**Title:** {title}")
        output.append(f"**Author:** {author} ({date_loc})")
        output.append(f"**Text Content:**\n{note_text}\n")
        output.append(f"**Tags:** {', '.join(tags_list)}")
        output.append(f"**Stats:** Likes: {likes} | Collections: {collections} | Comments: {comments}")
        
        if comments_list:
            output.append("\n**Top Comments:**")
            for c in comments_list:
                top_badge = "[TOP] " if c.get('is_top') else ""
                output.append(f"- {top_badge}**{c['author']}** ({c['date']} {c['location']}) [Likes: {c['likes']}]: {c['content']}")
                if c.get('reply'):
                    r = c['reply']
                    output.append(f"  - > **{r['author']}** ({r['date']} {r['location']}) [Likes: {r['likes']}]: {r['content']}")

        output.append("---------------------\n")
        
    except Exception as e:
        output.append(f"Failed to extract post details: {e}")
    
    result_str = "\n".join(output)
    print(result_str) # Keep printing for terminal monitoring
    return result_str

def close_post_details(page: Page):
    """
    Closes the currently open post detail modal.
    
    Args:
        page (Page): The Playwright page object.
        
    Behavior:
        1. Attempts to find and click the close button (.close-circle .close).
        2. If not found, falls back to pressing the 'Escape' key.
        3. Waits briefly for the UI to update.
    """
    print("Closing post details...")
    try:
        # Selector for the close button in the modal
        close_btn = page.locator(".close-circle .close").first
        if close_btn.is_visible():
            close_btn.click()
            print("Clicked close button.")
            time.sleep(1) # Wait for modal to close
        else:
            print("Close button not found. Trying Escape key.")
            page.keyboard.press("Escape")
            time.sleep(1)
            
    except Exception as e:
        print(f"Error closing post details: {e}")
