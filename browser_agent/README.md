# Browser Agent

This directory contains scripts for browser automation using Playwright with stealth capabilities, specifically tailored for Xiaohongshu (XHS) data extraction.

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

## Project Structure

The project has been refactored into a modular architecture for better maintainability and reusability.

*   **`browser_utils.py`**: 
    *   Handles browser initialization.
    *   Manages persistent contexts (cookies, login sessions).
    *   Applies stealth techniques (removing `navigator.webdriver`, custom user agent args).
*   **`xhs_actions.py`**: 
    *   Contains the core business logic for Xiaohongshu interactions.
    *   `search_xhs(page, query)`: robust search with input clearing.
    *   `extract_search_results(page)`: scrapes search result titles and likes.
    *   `extract_post_details(page)`: scrapes deep details including full text, tags, stats, and comments.
    *   `close_post_details(page)`: handles modal navigation.
*   **`xhs_search_test.py`**: 
    *   The main orchestration script that ties everything together.
    *   Demonstrates a complete workflow: Launch -> Search -> Extract List -> Click Post -> Extract Details -> Close -> Next Post.
*   **`bot_test.py`**: 
    *   A utility script to verify stealth capabilities against bot detection sites.

## Usage

### Run XHS Search & Extraction
This is the main entry point for the XHS automation workflow.

```powershell
python xhs_search_test.py
```

**Workflow:**
1.  Launches a persistent Chrome instance (you will stay logged in across runs).
2.  Navigates to Xiaohongshu.
3.  Searches for "AI Agent".
4.  Extracts the top search results to the console.
5.  Opens the 3rd post, extracts full details (including comments), and closes it.
6.  Opens the 4th post, extracts full details, and closes it.
7.  **Pauses** and waits for you to press `Enter` in the terminal to exit. This allows you to inspect the browser state.

### Run Bot Detection Test
Verifies that the browser configuration is not detected as a bot.

```powershell
python bot_test.py
```

## Key Features

### 1. Stealth Mode
-   **`--disable-blink-features=AutomationControlled`**: Removes the "controlled by automation" flag.
-   **`navigator.webdriver` Override**: Manually deletes the webdriver property via script injection.
-   **Persistent Context**: Uses `./chrome_user_data` to save your login session. You only need to scan the QR code once.

### 2. Robust Extraction
-   **Scoped Selectors**: Uses specific container IDs (e.g., `#noteContainer`) to avoid scraping unrelated text from the background feed.
-   **Data Normalization**: Automatically converts "赞" (Chinese for "Like") to "0" for consistent integer parsing.
-   **Comment Scraping**: Extracts parent comments and their top replies, handling "0 comments" cases gracefully.

### 3. Navigation Logic
-   **Modal Handling**: Smartly detects the close button or uses the `Escape` key to return to the feed.
-   **Input Clearing**: Checks for and clicks the "clear text" icon before typing new search queries.

## Developer Notes

-   **Modifying the Workflow**: Edit `xhs_search_test.py` to change search queries or the number of posts to scrape.
-   **Adding Actions**: Add new interaction functions to `xhs_actions.py` (e.g., `like_post`, `collect_post`).
-   **Browser Profile**: If you encounter issues, try deleting the `chrome_user_data` folder to reset the browser profile.
