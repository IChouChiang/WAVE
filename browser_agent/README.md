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
    *   **`launch_persistent_browser`**: Initializes the browser with persistent storage (cookies/login) and stealth settings.
    *   **`get_ip_location`**: Automatically detects the user's real-world location via IP to enable "Nearby" search filters.
    *   Manages persistent contexts (cookies, login sessions).
    *   Applies stealth techniques (removing `navigator.webdriver`, custom user agent args).
*   **`xhs_actions.py`**: 
    *   Contains the core business logic for Xiaohongshu interactions.
    *   `search_xhs(page, query)`: robust search with input clearing.
    *   `extract_search_results(page)`: scrapes search result titles and likes.
    *   `extract_post_details(page)`: scrapes deep details including full text, tags, stats, and comments.
    *   `close_post_details(page)`: handles modal navigation.
    *   `apply_search_filters(page, filters)`: applies search filters (Sort, Type, Time, Scope, Location).
*   **`deepseek_agent.py`**:
    *   **DeepSeek Agent**: A standalone agent script that uses the DeepSeek API (Thinking Mode) to autonomously explore XHS.
    *   Implements a tool-use loop where the LLM decides which browser actions to take based on user goals.
    *   Tools: `launch_browser`, `search`, `filter_results`, `get_results_list`, `open_post`, `get_post_details`, `close_post`.
*   **`xhs_mcp_server.py`**:
    *   **MCP Server Implementation**: Exposes the browser actions as Model Context Protocol (MCP) tools.
    *   Allows LLMs (like DeepSeek, Claude, etc.) to control the browser programmatically.
    *   Tools: `launch_browser`, `search`, `filter_results`, `get_search_results_list`, `open_post`, `get_post_details`, `close_post`.
*   **`tests/`**:
    *   **`xhs_search_test.py`**: Main orchestration script. Launch -> Search -> Extract List -> Click Post -> Extract Details -> Close -> Next Post.
    *   **`xhs_filter_test.py`**: Verifies search filter functionality (Sort, Type, Time, Scope, Location).
    *   **`xhs_debug_filter.py`**: Utility to freeze the page for inspecting dynamic filter components.
    *   **`bot_test.py`**: Verifies stealth capabilities against bot detection sites.
    *   **`test_mcp_simulation.py`**: Simulates an LLM calling the MCP tools to verify the full toolchain.

## Usage

### 1. DeepSeek Agent (Autonomous Mode)
Run the autonomous agent to explore XHS with natural language commands.
```powershell
python browser_agent/deepseek_agent.py
```
**Important**: This script requires a DeepSeek API key.
1.  Create a file named `ds_api.txt` in the `browser_agent` directory.
2.  Paste your API key into this file (just the key, no extra text).

### 2. MCP Server (Tool Mode)
Run the MCP server to expose tools to an MCP-compatible client (e.g., Claude Desktop, Cursor).
```powershell
python browser_agent/xhs_mcp_server.py
```

### 3. Run MCP Tool Simulation
Verifies that the MCP tools are working correctly by simulating an LLM interaction sequence.

```powershell
python browser_agent/tests/test_mcp_simulation.py
```

**Simulation Results (Verified 2025-12-04):**
The simulation successfully performed the following sequence:
1.  **Launch**: Opened persistent browser.
2.  **Search**: Searched for "DeepSeek".
3.  **Filter**: Applied "Sort by Latest" (排序依据=最新).
4.  **List**: Extracted top results (e.g., "V3.2正式版...").
5.  **Open**: Opened the first post.
6.  **Details**: Extracted full content, stats (Likes: 1163), and nested comments.
7.  **Close**: Closed the post modal.

### Run XHS Search & Extraction
This is the main entry point for the XHS automation workflow.

```powershell
python browser_agent/tests/xhs_search_test.py
```

**Workflow:**
1.  Launches a persistent Chrome instance (you will stay logged in across runs).
2.  Navigates to Xiaohongshu.
3.  Searches for "AI Agent".
4.  Extracts the top search results to the console.
5.  Opens the 3rd post, extracts full details (including comments), and closes it.
6.  Opens the 4th post, extracts full details, and closes it.
7.  **Pauses** and waits for you to press `Enter` in the terminal to exit. This allows you to inspect the browser state.

### Run Filter Test
Verifies that search filters work correctly.

```powershell
python browser_agent/tests/xhs_filter_test.py
```

### Run Bot Detection Test
Verifies that the browser configuration is not detected as a bot.

```powershell
python browser_agent/tests/bot_test.py
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
-   **Filter Application**: Supports applying multiple filters (Sort, Type, Time, Scope, Location) via the `apply_search_filters` function.

## Developer Notes

-   **Modifying the Workflow**: Edit scripts in `tests/` to change search queries or the number of posts to scrape.
-   **Adding Actions**: Add new interaction functions to `xhs_actions.py` (e.g., `like_post`, `collect_post`).
-   **Browser Profile**: If you encounter issues, try deleting the `chrome_user_data` folder to reset the browser profile.
