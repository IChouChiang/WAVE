# WAVE Project Instructions

## Project Overview
WAVE (Web Automation & Visual Editor) is a modular platform for web automation and content creation. It employs a "Manager of Managers" architecture where distinct toolsets (e.g., Xiaohongshu, IEEE Xplore) are packaged as Model Context Protocol (MCP) servers for LLM consumption.

### Architecture
- **Browser Agent (`browser_agent/`)**: Python backend for modular web automation.
  - **Toolsets**: 
    - `xhs_actions.py`: Xiaohongshu interactions.
    - `xplore_actions.py`: IEEE Xplore academic paper collection.
  - **MCP Servers**: Tools are packaged into domain-specific MCP servers (e.g., `xhs_mcp_server.py`) to be orchestrated by a higher-level manager.
  - **Prototypes**: `deepseek_agent.py` is a prototype for autonomous agent logic.
  - **Shared Logic**: `browser_utils.py` (Browser setup/stealth).
- **Frontend (`frontend/`)**: Next.js 16 (App Router) + React 19 + Tailwind CSS 4 application.
  - **Visual Editor**: Canva-like interface for content creation.
  - **Integration**: `app/api/ai/` contains endpoints for AI features.

## Critical Workflows

### Python Environment (CRITICAL)
**ALWAYS** activate the virtual environment before running any Python scripts or installing packages.
- **Windows (PowerShell)**: `.\browser_agent\venv\Scripts\Activate.ps1`
- **macOS/Linux**: `source browser_agent/venv/bin/activate`

### Running the Components
- **MCP Servers**: Run specific server scripts (e.g., `python browser_agent/xhs_mcp_server.py`).
- **Prototypes**: `python browser_agent/deepseek_agent.py` (Prototype Agent).
- **Tests**: `python browser_agent/tests/xhs_search_test.py`

### Frontend Development
- **Start**: `cd frontend && npm run dev`
- **Stack**: Next.js 16, React 19, Tailwind 4, Lucide React.

## Coding Conventions

### Python (Browser Agent)
- **Browser Launch**: ALWAYS use `browser_utils.launch_persistent_browser()` to ensure stealth and session persistence. Do not use raw `playwright.launch()`.
- **MCP Tool Design**: 
  - Functions in `*_actions.py` should be designed as stateless, atomic tools suitable for MCP exposure.
  - Use the global `BrowserState` class pattern to maintain browser context across multiple MCP tool calls.
- **Configuration**: Access secrets and settings via `browser_agent/config.py`.

### TypeScript (Frontend)
- **Styling**: Use Tailwind CSS 4 utility classes.
- **Icons**: Use `lucide-react` for all icons.
- **API Routes**: Located in `frontend/app/api/`. When implementing real AI logic, reference `docs/Backend_AI_Integration.md` for the expected JSON contract.

## Integration & Data Flow
- **Architecture**: The system uses a "Manager of Managers" approach. A central orchestrator (future) will delegate tasks to specific MCP servers (XHS, Xplore).
- **Frontend -> Backend**: The frontend expects to call AI services via `/api/ai/*`.
