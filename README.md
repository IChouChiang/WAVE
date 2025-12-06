# WAVE - Web Automation & Visual Editor

**WAVE** is a comprehensive platform for Xiaohongshu (XHS) content automation and creation, combining browser automation with an AI-powered visual editor.

## Project Overview

WAVE consists of two main components:

1. **Browser Agent** (`browser_agent/`) - Python-based automation for XHS data extraction and interaction
2. **Visual Frontend** (`frontend/`) - Next.js application for AI-assisted content creation

### Key Features
- **Autonomous Browser Agent**: Automated XHS exploration using DeepSeek AI with thinking mode
- **IEEE Xplore Integration**: Automated academic paper search and PDF download with anti-bot evasion
- **Canva-like Editor**: Visual interface for designing XHS posts with AI suggestions
- **MCP Integration**: Model Context Protocol server for LLM tool integration
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Stealth Automation**: Anti-detection browser automation with persistent sessions

## Project Structure

```
WAVE/
├── browser_agent/          # Python automation backend
│   ├── config.py           # Centralized configuration
│   ├── browser_utils.py    # Browser initialization
│   ├── xhs_actions.py      # XHS interaction logic
│   ├── xplore_actions.py   # IEEE Xplore interaction logic
│   ├── deepseek_xhs.py     # Autonomous AI agent for XHS
│   ├── deepseek_xplore.py  # Autonomous AI agent for IEEE Xplore
│   ├── xhs_mcp_server.py   # MCP server for XHS tools
│   ├── xplore_mcp_server.py # MCP server for IEEE Xplore tools
│   ├── tests/              # Test scripts
│   └── README.md           # Detailed setup guide
├── frontend/               # Next.js visual editor
│   ├── app/                # Next.js App Router
│   ├── docs/               # API documentation
│   └── README.md           # Frontend guide
└── docs/                   # Project documentation
```

## Quick Start

### Option 1: Start with Browser Agent (Recommended)
The browser agent is the core automation component. Start here to understand the XHS automation capabilities:

```bash
# Navigate to browser_agent
cd browser_agent

# Automated setup (choose based on your OS)
# Windows:
.\setup.ps1

# macOS/Linux:
chmod +x setup.sh
./setup.sh

# Run the autonomous agent
# IMPORTANT: You must activate the virtual environment first!
# Windows: .\venv\Scripts\Activate.ps1
# macOS/Linux: source venv/bin/activate
python deepseek_xhs.py
```

#### Important: Virtual Environment Activation
Before running any Python scripts, you must activate the virtual environment:

**Windows (PowerShell):**
```powershell
cd browser_agent
.\venv\Scripts\Activate.ps1
python deepseek_xhs.py
```

**macOS/Linux:**
```bash
cd browser_agent
source venv/bin/activate
python deepseek_xhs.py
```

**Common Error:** If you see `ModuleNotFoundError: No module named 'playwright'`, it means you forgot to activate the virtual environment.

#### API Key Setup
The browser agent requires a DeepSeek API key. You have two options:

**Option A: Using ds_api.txt (Recommended for personal use)**
1. Create a file named `ds_api.txt` in the `browser_agent` directory
2. Paste your DeepSeek API key into the file (just the key, no extra text)
3. Run the setup script - it will automatically load the key into `.env`

**Option B: Using .env file (Recommended for team collaboration)**
1. Copy `.env.example` to `.env`
2. Edit `.env` and set `DEEPSEEK_API_KEY=your_api_key_here`
3. Run the setup script

**Get your API key from:** https://platform.deepseek.com/api_keys

**Security Note:** Both `.env` and `ds_api.txt` are excluded from git via `.gitignore`

### Option 2: Start with Visual Frontend
The frontend provides a visual interface for content creation:

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Component Integration

### Current Integration Status
- **Frontend → Backend**: Frontend is designed to work with a Python backend on port 8000
- **Browser Agent**: Standalone automation system with MCP server capabilities
- **DeepSeek Agent**: Command-line interactive agent for XHS exploration

### Recommended Workflow
1. **Start with Browser Agent**: Test XHS automation using `deepseek_agent.py`
2. **Explore MCP Tools**: Run `xhs_mcp_server.py` to expose tools to LLM clients
3. **Develop Frontend**: Work on the visual editor while backend matures

## Tech Stack

### Browser Agent (Python)
- **Automation**: Playwright with stealth capabilities
- **AI Integration**: DeepSeek API with thinking mode
- **Protocol**: Model Context Protocol (MCP) server
- **Configuration**: Environment-based with cross-platform support

### Visual Frontend (Next.js)
- **Framework**: Next.js 16 (App Router)
- **UI**: Tailwind CSS, Lucide React
- **Drag & Drop**: React DnD
- **Language**: TypeScript

## Note
If the AI Chat or Publish features are not working, check that:
1.  The Python server is running on port 8000.
2.  There are no CORS issues (though the Next.js API route proxies requests to avoid this).

## Current Placeholders & Mock Data

The frontend currently contains several placeholders and fallback mechanisms to allow UI testing without a running backend.

### 1. AI Suggestions (`frontend/app/api/ai/suggestions`)
-   **Status**: Mocked.
-   **Behavior**: The API route currently returns an empty list.
-   **Fallback**: `AIDialog.tsx` uses hardcoded arrays (`singleElementSuggestions`, `multiElementSuggestions`, `globalSuggestions`) when no suggestions are returned from the API.

### 2. AI Modifications (`frontend/app/api/ai/apply`)
-   **Status**: Hybrid (Proxy + Fallback).
-   **Behavior**: Tries to forward requests to `http://127.0.0.1:8000/chat`.
-   **Fallback**: If the backend is offline, `App.tsx` executes local keyword-based logic (e.g., "make it bigger", "change color to red") to simulate AI changes.

### 3. Publishing (`frontend/app/api/ai/publish`)
-   **Status**: Proxy.
-   **Behavior**: Forwards requests to `http://127.0.0.1:8000/publish`.
-   **Note**: Hardcoded to localhost:8000.

### 4. Hardcoded URLs
-   The API routes currently point to `http://127.0.0.1:8000`. This should be moved to environment variables (`.env`) for production.
