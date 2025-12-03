from playwright.sync_api import Playwright, BrowserContext, Page

MAX_WIDTH = 1440
MAX_HEIGHT = 800

def launch_persistent_browser(p: Playwright, user_data_dir: str = "./chrome_user_data", headless: bool = False) -> tuple[BrowserContext, Page]:
    """
    Launches a persistent browser context with stealth settings.
    Returns the context and the first page.
    """
    print(f"Launching browser in persistent mode (User Data: {user_data_dir})...")
    
    context = p.chromium.launch_persistent_context(
        user_data_dir,
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled", 
            "--start-maximized",
        ],
        viewport={"width": MAX_WIDTH, "height": MAX_HEIGHT},
    )
    
    page = context.pages[0] if context.pages else context.new_page()
    
    # Apply stealth settings
    print("Applying manual stealth settings...")
    page.add_init_script("""
        if (Object.getPrototypeOf(navigator).webdriver) {
            delete Object.getPrototypeOf(navigator).webdriver;
        }
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
    """)
    
    return context, page
