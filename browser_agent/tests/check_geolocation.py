
import sys
import os
import time
from playwright.sync_api import sync_playwright

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from browser_utils import launch_persistent_browser

def check_geolocation():
    print("Checking Geolocation Permissions...")
    
    with sync_playwright() as p:
        try:
            context, page = launch_persistent_browser(p, user_data_dir="./chrome_user_data")
            page.goto("https://www.xiaohongshu.com/explore")
            time.sleep(2)
            
            print("\n--- Permission Status ---")
            # Check permission state
            perm_state = page.evaluate("""
                navigator.permissions.query({name:'geolocation'})
                .then(result => result.state)
            """)
            print(f"navigator.permissions.state: {perm_state}")
            
            print("\n--- Active Geolocation Check ---")
            # Try to get position
            try:
                pos = page.evaluate("""
                    new Promise((resolve, reject) => {
                        navigator.geolocation.getCurrentPosition(
                            pos => resolve({
                                lat: pos.coords.latitude, 
                                lng: pos.coords.longitude,
                                accuracy: pos.coords.accuracy
                            }),
                            err => reject(err.message),
                            {timeout: 5000}
                        )
                    })
                """)
                print(f"Success! Position: {pos}")
            except Exception as e:
                print(f"Failed to get position: {e}")

            print("\n-------------------------")
            print("Press Enter to exit.")
            input()
            context.close()
            
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    check_geolocation()
