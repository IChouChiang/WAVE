import time
from playwright.sync_api import sync_playwright

def main():
    print("Starting Playwright script...")
    
    with sync_playwright() as p:
        try:
            # Launch a new browser instance with stealth flags
            # We use launch() instead of connect_over_cdp() to ensure flags are applied correctly
            print("Launching browser with stealth flags...")
            browser = p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled", 
                ]
            )
            
            # Create a new page
            page = browser.new_page()
            
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
            
            # We don't close the browser here because it's a remote connection to a user's browser
            page.close()
            
        except Exception as e:
            print(f"An error occurred: {e}")
            print("\nTroubleshooting:")
            print("1. Ensure Chrome is running with: chrome.exe --remote-debugging-port=9222")
            print("2. Ensure no other debugger is connected to that port.")

if __name__ == "__main__":
    main()
