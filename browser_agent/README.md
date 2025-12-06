# Browser Agent

This directory contains scripts for browser automation using Playwright with stealth capabilities, specifically tailored for Xiaohongshu (XHS) data extraction and IEEE Xplore academic research.

## Key Features
- **Xiaohongshu (XHS) Automation**: Search, filter, and extract post details.
- **IEEE Xplore Automation**: Search for academic papers and download PDFs (bypassing anti-bot protections).
- **DeepSeek AI Integration**: Autonomous agent capabilities using DeepSeek's reasoning models.
- **MCP Server**: Exposes automation tools via the Model Context Protocol.

## Quick Start

### 1. Setup Environment
```bash
# On Windows (PowerShell):
.\setup.ps1
```

### 2. Launch Bot Browser (One-Time Login)
The agent uses a dedicated Chrome profile to maintain login sessions. You must launch this browser and log in manually once.

```powershell
# Launch the Bot Browser
.\launch_debug_chrome.ps1
```
*A Chrome window will open. Log in to Xiaohongshu and IEEE Xplore in this window.*

### 3. Run Tests
With the Bot Browser open, run the tests to verify everything works:

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Test 1: Verify Bot Stealth (should show all green)
python tests/user_bot_test.py

# Test 2: Verify Xiaohongshu Search & Detail Access
python tests/user_xhs_test.py

# Test 3: Verify IEEE Xplore PDF Download
python tests/user_pdf_test.py
```

### 4. Run Agents
```bash
# Run the DeepSeek Autonomous Agent
python deepseek_agent.py

# Start the MCP Server (for external tools)
python xhs_mcp_server.py
```

## Python Environment Setup

### Common Error: ModuleNotFoundError
If you see errors like `ModuleNotFoundError: No module named 'playwright'`, it means you're not using the virtual environment:

```powershell
# ❌ WRONG - Running without activating virtual environment
python .\deepseek_agent.py
# Error: ModuleNotFoundError: No module named 'playwright'

# ✅ CORRECT - First activate the virtual environment
.\venv\Scripts\Activate.ps1
python .\deepseek_agent.py
# Success: Agent starts normally
```

### Solution: Activate Virtual Environment
Always activate the virtual environment before running Python scripts:

#### Windows (PowerShell)
```powershell
# Navigate to browser_agent directory
cd browser_agent

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Your prompt should change to show (venv)
# Now you can use python directly
python deepseek_agent.py
python tests/user_xhs_test.py
python --version
```

#### macOS/Linux
```bash
# Navigate to browser_agent directory
cd browser_agent

# Activate virtual environment
source venv/bin/activate

# Your prompt should change to show (venv)
# Now you can use python directly
python deepseek_agent.py
python tests/user_xhs_test.py
python --version
```

#### Alternative: Direct Python Path
If you prefer not to activate the environment, use the full path:

**Windows:**
```powershell
.\venv\Scripts\python.exe tests/xhs_search_test.py
```

**macOS/Linux:**
```bash
./venv/bin/python tests/xhs_search_test.py
```

### Deactivating the Environment
When you're done, deactivate the virtual environment:
```bash
deactivate
```

## Configuration

### Environment Variables
Create a `.env` file in the `browser_agent` directory with the following settings:

```env
# DeepSeek API Configuration (Required for deepseek_agent.py)
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Browser Configuration
CHROME_USER_DATA_DIR=./chrome_user_data
BROWSER_HEADLESS=false
BROWSER_WIDTH=1440
BROWSER_HEIGHT=800

# Xiaohongshu Configuration
XHS_EXPLORE_URL=https://www.xiaohongshu.com/explore

# MCP Server Configuration
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8000
```

### API Key Setup
The browser agent supports two methods for API key management:

**Method 1: Using ds_api.txt (Recommended for personal use)**
1. Create a file named `ds_api.txt` in the `browser_agent` directory
2. Paste your DeepSeek API key into the file (just the key, no extra text)
3. Run the setup script - it will automatically:
   - Detect `ds_api.txt`
   - Load the API key
   - Update `.env` file with the key
   - Configure everything automatically

**Method 2: Using .env file (Recommended for team collaboration)**
1. Copy `.env.example` to `.env`
2. Edit `.env` and set `DEEPSEEK_API_KEY=your_api_key_here`
3. Run the setup script

**Get your API key from:** https://platform.deepseek.com/api_keys

**Security Notes:**
- Both `.env` and `ds_api.txt` are excluded from git via `.gitignore`
- Never commit these files to version control
- The system automatically loads API keys from `ds_api.txt` if `.env` doesn't have one

## Project Structure

```
browser_agent/
├── config.py              # Configuration management
├── browser_utils.py       # Browser initialization and utilities
├── xhs_actions.py         # Xiaohongshu interaction logic
├── deepseek_agent.py      # Autonomous AI agent using DeepSeek API
├── xhs_mcp_server.py      # MCP server for tool integration
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment configuration
├── README.md             # This file
└── tests/                # Test scripts
    ├── xhs_search_test.py
    ├── xhs_filter_test.py
    ├── bot_test.py
    └── ...
```

### Core Modules

*   **`config.py`** - Centralized configuration management using environment variables
*   **`browser_utils.py`** - Browser initialization with stealth settings and persistent sessions
*   **`xhs_actions.py`** - Core Xiaohongshu interaction logic with:
    - **Robust Extraction**: Scoped selectors using container IDs, data normalization, comment scraping
    - **Navigation Logic**: Modal handling, input clearing, filter application
    - **Search & Filtering**: Multi-filter support (Sort, Type, Time, Scope, Location)
*   **`deepseek_agent.py`** - Autonomous AI agent using DeepSeek API with thinking mode
*   **`xhs_mcp_server.py`** - MCP server exposing browser tools to LLM clients

## Usage

### DeepSeek Agent (Autonomous Mode)
Run the autonomous agent to explore XHS with natural language commands:
```bash
python deepseek_agent.py
```

**Requirements**: DeepSeek API key in `.env` file

### MCP Server (Tool Mode)
Run the MCP server to expose tools to MCP-compatible clients (Claude Desktop, Cursor, etc.):
```bash
python xhs_mcp_server.py
```

### Testing
```bash
# Basic browser test
python tests/xhs_search_test.py

# Filter functionality test
python tests/xhs_filter_test.py

# Bot detection test
python tests/bot_test.py

# MCP tool simulation
python tests/test_mcp_simulation.py
```
## Cross-Platform Support

The project is designed to work on Windows, macOS, and Linux. All hardcoded paths have been replaced with configuration variables.

### Key Features
- **Unified Configuration**: All platform-specific paths are managed through `.env` file
- **Automated Setup**: One-click setup scripts for each platform
- **Consistent API**: Same Python code works across all platforms

### Configuration Files
- **`.env`**: Local environment configuration (not committed to git)
- **`.env.example`**: Example configuration template
- **`config.py`**: Centralized configuration loader

## Development

### Adding New Features
1. Add configuration variables to `.env.example`
2. Load them in `config.py`
3. Use `config.variable_name` in your code
4. Update README with usage instructions

### Testing Changes
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python tests/xhs_search_test.py
```

### Developer Notes
- **Modifying Workflows**: Edit scripts in `tests/` to change search queries or the number of posts to scrape
- **Adding Actions**: Add new interaction functions to `xhs_actions.py` (e.g., `like_post`, `collect_post`)
- **Browser Profile**: If you encounter issues, try deleting the `chrome_user_data` folder to reset the browser profile
- **Configuration**: All paths are configurable via `.env` file for cross-platform compatibility

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **"DeepSeek API key not found"**
   - Check that `.env` file exists in `browser_agent` directory
   - Verify `DEEPSEEK_API_KEY` is set in `.env`
   - Get API key from: https://platform.deepseek.com/api_keys

3. **Browser won't launch**
   ```bash
   playwright install chromium
   ```

4. **Permission errors (macOS/Linux)**
   ```bash
   chmod +x venv/bin/activate
   ```

### Debug Mode
Enable debug logging by setting in `.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## Support

### Getting Help
- Check the [troubleshooting section](#-troubleshooting)
- Review configuration in `.env` file
- Enable debug mode for detailed logs

### Reporting Issues
When reporting issues, please include:
1. Operating system (Windows/macOS/Linux)
2. Python version (`python --version`)
3. Configuration (redacted `.env` file)
4. Error messages and logs

## License

This project is part of the WAVE repository. See the main repository for license information.

---

**Happy browsing!**
