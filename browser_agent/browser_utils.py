from playwright.sync_api import Playwright, BrowserContext, Page
import json
import urllib.request
import os
import sys

from typing import Optional

# Add current directory to path for config import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import settings as config

def get_ip_location():
    """
    Detects the user's physical location via their public IP address.
    
    Returns:
        dict: A dictionary containing 'latitude' and 'longitude'.
              Defaults to Shanghai coordinates if detection fails.
    """
    try:
        with urllib.request.urlopen("http://ip-api.com/json/", timeout=3) as url:
            data = json.loads(url.read().decode())
            if data.get("status") == "success":
                print(f"Detected IP Location: {data['city']}, {data['country']} ({data['lat']}, {data['lon']})")
                return {"latitude": data["lat"], "longitude": data["lon"]}
    except Exception as e:
        print(f"Warning: Could not detect IP location ({e}). Using default.")
    return {"latitude": 31.2304, "longitude": 121.4737} # Default to Shanghai

def launch_persistent_browser(p: Playwright, user_data_dir: Optional[str] = None, headless: Optional[bool] = None) -> tuple[BrowserContext, Page]:
    """
    Launches a persistent browser context with stealth settings and auto-detected location.
    
    Args:
        p (Playwright): The Playwright instance.
        user_data_dir (Optional[str]): Path to the directory for storing user data (cookies, cache).
                            If None, uses config.CHROME_USER_DATA_DIR.
        headless (Optional[bool]): Whether to run the browser in headless mode.
                        If None, uses config.BROWSER_HEADLESS.
        
    Returns:
        tuple[BrowserContext, Page]: The browser context and the first page object.
        
    Features:
        - Persistent Context: Saves login state and cookies.
        - Stealth Mode: Hides automation flags (navigator.webdriver).
        - Auto-Location: Injects the user's real IP-based geolocation to enable "Nearby" features.
    """
    # Use config values if parameters are not provided
    if user_data_dir is None:
        user_data_dir = str(config.get_chrome_user_data_dir())
    if headless is None:
        headless = config.BROWSER_HEADLESS
    
    print(f"Launching browser in persistent mode (User Data: {user_data_dir})...")
    
    # Detect location
    location = get_ip_location()
    print(f"Using location: {location}")

    # Ensure downloads directory exists
    downloads_path = config.PROJECT_ROOT / config.DOWNLOADS_DIR
    if not downloads_path.exists():
        downloads_path.mkdir(parents=True, exist_ok=True)
    print(f"Downloads directory: {downloads_path}")

    launch_args = {
        "user_data_dir": user_data_dir,
        "headless": headless,
        "args": [
            "--disable-blink-features=AutomationControlled", 
            "--start-maximized",
        ],
        "viewport": {"width": config.BROWSER_WIDTH, "height": config.BROWSER_HEIGHT},
        "permissions": ["geolocation"],
        "geolocation": location,
        "accept_downloads": True,
        "downloads_path": str(downloads_path), # Set default download path
    }

    # Use custom executable path if provided in config
    if config.CHROME_EXECUTABLE_PATH:
        print(f"Using custom browser executable: {config.CHROME_EXECUTABLE_PATH}")
        launch_args["executable_path"] = config.CHROME_EXECUTABLE_PATH
        launch_args["channel"] = "chrome" # Hint to use chrome channel if path is provided

    context = p.chromium.launch_persistent_context(**launch_args)
    
    # Define download handler to save files with correct names
    def handle_download(download):
        print(f"Download started: {download.suggested_filename}")
        try:
            # Wait for the download to complete
            # Save to the configured downloads directory with the suggested filename
            file_path = downloads_path / download.suggested_filename
            download.save_as(file_path)
            print(f"✓ Download complete: {file_path}")
        except Exception as e:
            print(f"❌ Download failed: {e}")

    # Attach download handler to all pages
    context.on("page", lambda page: page.on("download", handle_download))
    
    page = context.pages[0] if context.pages else context.new_page()
    
    # Attach to the initial page as well
    page.on("download", handle_download)
    
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
