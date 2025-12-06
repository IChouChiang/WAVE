"""
Bot Detection Verification Script

This script launches the browser with the configured stealth settings and navigates 
to https://bot.sannysoft.com/ to verify that the automation is not detected as a bot.
"""
import sys
import os
import time
from playwright.sync_api import sync_playwright


# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings as config

from browser_utils import launch_persistent_browser

def main():
    print("Starting Playwright script...")
    
    with sync_playwright() as p:
        try:
            # Launch browser using the utility function
            context, page = launch_persistent_browser(p)
            
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
