# Browser Agent

This directory contains scripts for browser automation using Playwright with stealth capabilities.

## Setup

1.  **Create Virtual Environment**:
    ```powershell
    cd browser_agent
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```

2.  **Install Dependencies**:
    ```powershell
    pip install -r requirements.txt
    playwright install chromium
    ```

## Usage

### Run the Script
The script now launches its own browser instance with specific flags to avoid detection. You do **not** need to launch Chrome manually anymore.

```powershell
python bot_test.py
```

## Success Status (Verified 2025-12-03)
The script successfully passes bot detection checks on `https://bot.sannysoft.com/`.

### Implemented Method
1.  **Launch Arguments**: 
    -   `headless=False`: Running in a visible window is less suspicious than headless mode.
    -   `--disable-blink-features=AutomationControlled`: This critical flag removes the "Chrome is being controlled by automated test software" infobar and internal flags.
2.  **Persistent Context**:
    -   Uses `launch_persistent_context` with a local user data directory (`./chrome_user_data`).
    -   This maintains cookies, cache, and local storage across sessions, simulating a real user profile.
3.  **Script Injection**: 
    -   We use `page.add_init_script` to manually delete and override `navigator.webdriver` before the page loads.
    -   This prevents the site from detecting the standard Selenium/Playwright property.

## Features
-   **Stealth Mode**: 
    -   Uses `--disable-blink-features=AutomationControlled` flag.
    -   Manually patches `navigator.webdriver` and other properties.
-   **Headed Mode**: Runs in a visible window (`headless=False`).
-   **Persistent Profile**: Saves login state and cookies to `./chrome_user_data`.
-   **Fixed Viewport**: Configured to 1440x900 to ensure consistent rendering across tabs.
-   **Bot Detection Test**: Navigates to `https://bot.sannysoft.com/` to verify stealth effectiveness.

### Scripts
-   **`bot_test.py`**: Verifies stealth capabilities against bot detection sites.
-   **`xhs_search_test.py`**: 
    -   Performs search operations on Xiaohongshu.
    -   Handles clearing existing search text (detects and clicks the close icon).
    -   **Extracts Results**: Scrapes the top 15 posts (Title and Like Count) and outputs them as a Markdown table.
    -   Keeps the browser open for manual monitoring (Press Ctrl+C to exit).

## 📝 Todo
-   [ ] Make viewport size flexible/responsive to fit the user's actual screen resolution automatically.
