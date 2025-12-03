import time
from playwright.sync_api import sync_playwright

MAX_WIDTH = 1440
MAX_HEIGHT = 800

def search_xhs(page, query):
    print(f"Searching for: {query}")
    
    # 1. Check for close icon (clear button) and click if it exists
    # The close icon appears when there is text in the input
    # We use a specific selector to avoid matching other close icons on the page (e.g. modals)
    try:
        close_icon = page.locator(".input-box .close-icon")
        if close_icon.is_visible(timeout=1000):
            print("Clearing existing text...")
            close_icon.click()
            time.sleep(0.5) # Short wait for UI update
    except Exception:
        # Ignore timeout or other errors if icon isn't found
        pass
    
    # 2. Type the query
    search_input = page.locator("#search-input")
    search_input.click()
    search_input.fill(query)
    print(f"Typed: {query}")
    
    # 3. Submit search (Press Enter)
    search_input.press("Enter")
    print("Pressed Enter to search")
    
    # Optional: Click search button (commented out as Enter is more robust against overlays)
    # search_button = page.locator(".search-icon")
    # search_button.click()
    # print("Clicked search button")
    
    # Wait for results to load
    # networkidle is too strict for XHS, using sleep + selector wait
    time.sleep(2) 
    try:
        page.wait_for_selector(".footer", timeout=10000)
        print("Search results loaded (found .footer)")
    except:
        print("Warning: Timeout waiting for results")
    
    # Extract and display results
    extract_search_results(page)

def extract_search_results(page, max_results=15):
    print(f"\n### Top {max_results} Results for current search")
    print("| Title | Likes |")
    print("| --- | --- |")
    
    # Wait for footers to be present
    try:
        page.wait_for_selector(".footer", timeout=5000)
    except:
        print("No results found.")
        return

    # Get all footer elements
    # Note: .all() returns a list of locators. 
    # In a real app, we might need to scroll to load more if 15 aren't visible, 
    # but XHS usually loads a batch initially.
    footers = page.locator(".footer").all()
    
    count = 0
    for footer in footers:
        if count >= max_results:
            break
            
        try:
            # Extract title
            # The snippet shows <a class="title"><span>...</span></a>
            title_el = footer.locator(".title span").first
            title = title_el.inner_text() if title_el.is_visible() else "No Title"
            
            # Extract likes
            # The snippet shows <span class="like-wrapper"><span class="count">12</span></span>
            like_el = footer.locator(".like-wrapper .count").first
            likes = like_el.inner_text() if like_el.is_visible() else "0"
            
            # Sanitize title for markdown table (remove pipes, newlines)
            title = title.replace("|", "-").replace("\n", " ").strip()
            
            print(f"| {title} | {likes} |")
            count += 1
        except Exception as e:
            print(f"Error extracting item: {e}")
            continue
    print("\n")

def extract_post_details(page):
    print("\n### Post Details Extraction")
    
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
            print(f"Error extracting basic info: {e}")
        
        # 1. Extract Text
        # Selector: #detail-desc .note-text span
        note_text = ""
        try:
            # The text is usually in the first span of .note-text
            text_el = container.locator("#detail-desc .note-text span").first
            if text_el.is_visible():
                note_text = text_el.inner_text().strip()
        except Exception as e:
            print(f"Error extracting text: {e}")
            
        # 2. Extract Tags
        tags_list = []
        try:
            # Find all elements with id="hash-tag" inside container
            tags = container.locator("#hash-tag").all()
            
            if not tags:
                # Fallback
                tags = container.locator("a.tag").all()
            
            for tag in tags:
                if tag.is_visible():
                    text = tag.inner_text().strip()
                    if text.startswith("#"):
                        tags_list.append(text)
        except Exception as e:
            print(f"Error extracting tags: {e}")

        # 3. Extract Stats (Likes, Collections, Comments)
        likes = "0"
        collections = "0"
        comments = "0"
        
        try:
            # Likes: .like-wrapper .count
            like_el = container.locator(".like-wrapper .count").first
            if like_el.is_visible():
                likes = like_el.inner_text()
                
            # Collections: .collect-wrapper .count
            collect_el = container.locator(".collect-wrapper .count").first
            if collect_el.is_visible():
                collections = collect_el.inner_text()
                
            # Comments: .chat-wrapper .count
            chat_el = container.locator(".chat-wrapper .count").first
            if chat_el.is_visible():
                comments = chat_el.inner_text()
        except Exception as e:
            print(f"Error extracting stats: {e}")
            
        # 4. Extract Comments
        comments_list = []
        try:
            # Parse comment count to decide if we should look for comments
            comment_count_int = 0
            if comments.isdigit():
                comment_count_int = int(comments)
            
            if comment_count_int > 0:
                print("Extracting comments...")
                
                # Locate parent comments
                # Wait for at least one if count > 0
                try:
                    container.locator(".parent-comment").first.wait_for(state="visible", timeout=3000)
                except:
                    pass # Proceed anyway

                parent_comments = container.locator(".parent-comment").all()[:5]
                
                for i, pc in enumerate(parent_comments):
                    c_data = {}
                    try:
                        # Parent Comment Details
                        c_data['author'] = pc.locator(".author .name").first.inner_text()
                        c_data['content'] = pc.locator(".content .note-text").first.inner_text()
                        
                        # Date & Location
                        # Date is usually the first span in .date
                        date_el = pc.locator(".info .date span").first
                        c_data['date'] = date_el.inner_text() if date_el.is_visible() else ""
                        
                        loc_el = pc.locator(".info .date .location").first
                        c_data['location'] = loc_el.inner_text() if loc_el.is_visible() else ""
                        
                        # Likes
                        like_el = pc.locator(".interactions .like .count").first
                        likes_text = like_el.inner_text() if like_el.is_visible() else "0"
                        c_data['likes'] = "0" if likes_text.strip() == "赞" else likes_text
                        
                        # Top Label
                        top_label = pc.locator(".labels .top").first
                        c_data['is_top'] = top_label.is_visible()
                        
                        # Inner Comment (Reply)
                        c_data['reply'] = None
                        # Check for sub-comments
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
                        print(f"Error extracting comment {i}: {e}")
                        
        except Exception as e:
            print(f"Error in comment extraction block: {e}")

        # Format as Markdown
        print("\n--- Post Analysis ---")
        print(f"**Title:** {title}")
        print(f"**Author:** {author} ({date_loc})")
        print(f"**Text Content:**\n{note_text}\n")
        print(f"**Tags:** {', '.join(tags_list)}")
        print(f"**Stats:** Likes: {likes} | Collections: {collections} | Comments: {comments}")
        
        if comments_list:
            print("\n**Top Comments:**")
            for c in comments_list:
                top_badge = "[TOP] " if c.get('is_top') else ""
                print(f"- {top_badge}**{c['author']}** ({c['date']} {c['location']}) [Likes: {c['likes']}]: {c['content']}")
                if c.get('reply'):
                    r = c['reply']
                    print(f"  - > **{r['author']}** ({r['date']} {r['location']}) [Likes: {r['likes']}]: {r['content']}")

        print("---------------------\n")
        
    except Exception as e:
        print(f"Failed to extract post details: {e}")

def main():
    print("Starting XHS Search Test...")
    
    with sync_playwright() as p:
        try:
            # Launch persistent context (reusing the setup from bot_test.py)
            user_data_dir = "./chrome_user_data"
            print(f"Launching browser in persistent mode (User Data: {user_data_dir})...")
            
            context = p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled", 
                    "--start-maximized",
                ],
                viewport={"width": MAX_WIDTH, "height": MAX_HEIGHT},
            )
            
            page = context.pages[0] if context.pages else context.new_page()
            
            # Apply stealth settings
            page.add_init_script("""
                if (Object.getPrototypeOf(navigator).webdriver) {
                    delete Object.getPrototypeOf(navigator).webdriver;
                }
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
            """)
            
            # 1. Navigate to Explore page
            url = "https://www.xiaohongshu.com/explore"
            print(f"Navigating to {url}...")
            page.goto(url)
            page.wait_for_load_state("domcontentloaded")
            
            # 2. First Search
            search_xhs(page, "github学生认证教程")
            time.sleep(3) # Let user see the result
            
            # 3. Second Search (Testing clear functionality)
            search_xhs(page, "openreview数据集")
            
            # 4. Click the 3rd post (Index 2)
            print("\nClicking the 3rd post to open details...")
            try:
                # The cover is the clickable image area defined by class "cover"
                # We use .nth(2) because it's 0-indexed
                # We wait for the element to be visible first
                target_cover = page.locator(".cover").nth(2)
                target_cover.wait_for(state="visible", timeout=5000)
                target_cover.click()
                print("Clicked 3rd post.")
                
                # Wait a bit to see the effect (modal opening)
                time.sleep(5)
                print("Detail view should be open now.")

                # 5. Extract Details (Text, Tags, Stats)
                extract_post_details(page)
                
            except Exception as e:
                print(f"Failed to interact with post details: {e}")
            
            print("Test completed successfully.")
            print("Browser remains open for monitoring. Press Ctrl+C to exit script (which will close browser).")
            
            # Keep script running indefinitely to prevent browser closure
            while True:
                time.sleep(1)
            
            # context.close() # Unreachable, but context manager will close on exit
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
