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
2.  **Script Injection**: 
    -   We use `page.add_init_script` to manually delete and override `navigator.webdriver` before the page loads.
    -   This prevents the site from detecting the standard Selenium/Playwright property.

## Features
-   **Stealth Mode**: 
    -   Uses `--disable-blink-features=AutomationControlled` flag.
    -   Manually patches `navigator.webdriver` and other properties.
-   **Headed Mode**: Runs in a visible window (`headless=False`).
-   **Bot Detection Test**: Navigates to `https://bot.sannysoft.com/` to verify stealth effectiveness.
