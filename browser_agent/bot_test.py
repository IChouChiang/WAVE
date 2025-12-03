import time
from playwright.sync_api import sync_playwright

MAX_WIDTH = 1440
MAX_HEIGHT = 800

def main():
    print("Starting Playwright script...")
    
    with sync_playwright() as p:
        try:
            # Launch a persistent browser context (normal window, not incognito)
            user_data_dir = "./chrome_user_data"
            print(f"Launching browser in persistent mode (User Data: {user_data_dir})...")
            
            context = p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled", 
                    "--start-maximized",
                ],
                # Set the viewport for the entire context (all pages/tabs)
                # This ensures new tabs inherit this size instead of reverting to default.
                # Note: 'no_viewport=True' (or viewport=None) allows the page to fill the window,
                # but if you want a specific fixed resolution, set it here.
                viewport={"width": MAX_WIDTH, "height": MAX_HEIGHT},
            )
            
            # Get the default page
            page = context.pages[0] if context.pages else context.new_page()

            # page.set_viewport_size(...) is no longer needed as it's set globally above
            
            # Apply manual stealth settings via init scripts
            print("Applying manual stealth settings...")
            
            # 1. Mask navigator.webdriver (Enhanced version)
            page.add_init_script("""
                // Remove the 'webdriver' property from the navigator prototype
                if (Object.getPrototypeOf(navigator).webdriver) {
                    delete Object.getPrototypeOf(navigator).webdriver;
                }
                
                // Hard override just in case
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            # 2. Mock languages (optional, but good practice)
            page.add_init_script("""
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)
            
            # Navigate to the bot detection test site
            target_url = "https://bot.sannysoft.com/"
            print(f"Navigating to {target_url}...")
            page.goto(target_url)
            
            print("Page loaded. Check the browser window for results.")
            print("Press Enter in this terminal to close the script (browser will remain open)...")
            input()
            
            context.close()
            
        except Exception as e:
            print(f"An error occurred: {e}")
            print("\nTroubleshooting:")
            print("1. Ensure no other Chrome instances are locking the './chrome_user_data' directory.")

if __name__ == "__main__":
    main()
