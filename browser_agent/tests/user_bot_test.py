"""
User Browser Bot Test

This script launches the user's actual Chrome browser (with their profile)
and navigates to a bot detection site to verify stealth capabilities.
"""
import sys
import os
import time
from playwright.sync_api import sync_playwright

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the new user browser utility
from user_browser_utils import launch_user_browser

def main():
    print("============================================================")
    print("USER BROWSER BOT TEST")
    print("============================================================")
    print("This test will launch your ACTUAL Chrome browser.")
    print("Please ensure all Chrome windows are CLOSED before continuing.")
    print("============================================================")
    
    # Simple confirmation to prevent accidental crashes
    print("Waiting 3 seconds before starting...")
    time.sleep(3)
    
    with sync_playwright() as p:
        try:
            # Launch user's browser
            context, page = launch_user_browser(p, headless=False)
            
            # Navigate to the bot detection test site
            target_url = "https://bot.sannysoft.com/"
            print(f"Navigating to {target_url}...")
            page.goto(target_url)
            
            print("\nTest running. Please inspect the browser window.")
            print("Look for 'WebDriver' -> 'missing' (green).")
            print("Look for 'User Agent' -> (should look normal).")
            
            print("Browser will remain open for 30 seconds...")
            time.sleep(30)
            
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
