import os
import sys
import platform
from pathlib import Path
from typing import Optional
from playwright.sync_api import Playwright, BrowserContext, Page

# Add current directory to path for config import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import settings as config

def get_system_chrome_path() -> Optional[str]:
    """Attempts to find the system Google Chrome executable."""
    # Check config first
    if config.CHROME_EXECUTABLE_PATH and os.path.exists(config.CHROME_EXECUTABLE_PATH):
        return config.CHROME_EXECUTABLE_PATH

    system = platform.system()
    if system == "Windows":
        paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
        for path in paths:
            if os.path.exists(path):
                return path
    elif system == "Darwin":  # macOS
        path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(path):
            return path
    elif system == "Linux":
        paths = ["/usr/bin/google-chrome", "/usr/bin/google-chrome-stable"]
        for path in paths:
            if os.path.exists(path):
                return path
    return None

def get_system_user_data_dir() -> Optional[str]:
    """Attempts to find the default system Chrome User Data Directory."""
    system = platform.system()
    if system == "Windows":
        path = os.path.expandvars(r"%LocalAppData%\Google\Chrome\User Data")
        if os.path.exists(path):
            return path
    elif system == "Darwin":
        path = os.path.expanduser("~/Library/Application Support/Google/Chrome")
        if os.path.exists(path):
            return path
    elif system == "Linux":
        path = os.path.expanduser("~/.config/google-chrome")
        if os.path.exists(path):
            return path
    return None

import subprocess
import time
import requests

def is_port_open(port: int) -> bool:
    try:
        response = requests.get(f"http://localhost:{port}/json/version", timeout=1)
        return response.status_code == 200
    except:
        return False

def launch_user_browser(p: Playwright, headless: bool = False) -> tuple[BrowserContext, Page]:
    """
    Launches (or connects to) the system's Google Chrome with the user's default profile.
    
    Strategy:
    1. Checks if Chrome is already running with remote debugging on port 9222.
    2. If not, launches Chrome with --remote-debugging-port=9222.
    3. Connects to the browser via CDP (Chrome DevTools Protocol).
    """
    executable_path = get_system_chrome_path()
    
    # Use a local folder for the bot's user profile
    # This avoids conflicts with the main system profile while still being persistent
    base_dir = os.path.dirname(os.path.abspath(__file__))
    user_data_dir = os.path.join(base_dir, "user_chrome_profile")
    
    # Ensure directory exists
    if not os.path.exists(user_data_dir):
        os.makedirs(user_data_dir)
        
    debug_port = 9223
    
    if not executable_path:
        raise FileNotFoundError("Could not find Google Chrome executable.")

    # 1. Check if we can already connect
    if is_port_open(debug_port):
        print(f"✅ Chrome is already running on port {debug_port}. Connecting...")
        try:
            browser = p.chromium.connect_over_cdp(f"http://localhost:{debug_port}")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()
            return context, page
        except Exception as e:
            print(f"⚠️  Port {debug_port} is open but connection failed: {e}")
            print("   Retrying launch...")

    print(f"🚀 Launching System Chrome on port {debug_port}...")
    print(f"📂 User Data: {user_data_dir}")
    print("⚠️  Please ensure no other Chrome windows are open, or this might fail.")
    
    cmd = [
        f'"{executable_path}"',
        f"--remote-debugging-port={debug_port}",
        "--no-first-run",
        "--no-default-browser-check"
    ]
    
    if user_data_dir:
        cmd.append(f'--user-data-dir="{user_data_dir}"')
        
    # Construct the full command string for shell execution
    full_cmd = " ".join(cmd)
    print(f"Executing: {full_cmd}")
    
    # Launch as a detached process
    # Use shell=True to ensure the command is executed properly on Windows
    subprocess.Popen(full_cmd, shell=True)
    
    # Wait for browser to start listening
    print("Waiting for Chrome to start...")
    for i in range(10):
        time.sleep(1)
        if is_port_open(debug_port):
            print("✓ Chrome is ready.")
            break
    else:
        print(f"\n❌ Chrome failed to start debugging port {debug_port}.")
        print("   Suggestion: Run 'browser_agent/launch_debug_chrome.ps1' manually to debug.")
        raise TimeoutError(f"Chrome failed to start debugging port {debug_port}.")

    # 2. Connect to the browser
    try:
        browser = p.chromium.connect_over_cdp(f"http://localhost:{debug_port}")
        
        # Get the default context (user profile)
        context = browser.contexts[0]
        
        # Get the first page or create new one
        page = context.pages[0] if context.pages else context.new_page()
        
        return context, page
        
    except Exception as e:
        print(f"❌ Failed to connect to Chrome: {e}")
        raise e
