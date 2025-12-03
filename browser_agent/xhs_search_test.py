import time
from playwright.sync_api import sync_playwright

MAX_WIDTH = 1440
MAX_HEIGHT = 900

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
    
    # 3. Click search button
    search_button = page.locator(".search-icon")
    search_button.click()
    print("Clicked search button")
    
    # Wait for results to load (simple wait for now, can be improved to wait for specific result elements)
    page.wait_for_load_state("networkidle")
    print("Search results loaded (networkidle)")
    
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
            time.sleep(3) # Let user see the result
            
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
