import os
import sys
import json
import time
from typing import Optional
from openai import OpenAI
from playwright.sync_api import sync_playwright, Page, BrowserContext

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_browser_utils import launch_user_browser
from xplore_actions import (
    search_xplore, 
    document_download_xplore, 
    search_extract_xplore, 
    navigate_to_page_xplore, 
    document_page_xplore
)
from config import settings as config

# --- Configuration ---
# API Key is loaded from environment variables or config
BASE_URL = config.DEEPSEEK_BASE_URL
MODEL_NAME = "deepseek-reasoner"  # Using Thinking Mode (R1) for complex reasoning

# --- State Management ---
class BrowserState:
    playwright = None
    context: Optional[BrowserContext] = None
    page: Optional[Page] = None

state = BrowserState()

# --- Tool Implementations ---

def launch_browser_tool():
    """Connects to the persistent user browser session."""
    if state.page:
        return "Browser is already connected."
    try:
        state.playwright = sync_playwright().start()
        state.context, state.page = launch_user_browser(state.playwright)
        state.page.goto("https://ieeexplore.ieee.org/Xplore/home.jsp")
        return "Browser connected successfully. You are on the IEEE Xplore home page."
    except Exception as e:
        return f"Failed to connect to browser: {str(e)}"

def search_tool(query: str):
    """Searches for a keyword on IEEE Xplore."""
    if not state.page: return "Error: Browser not connected."
    try:
        search_xplore(state.page, query)
        return f"Search for '{query}' completed. Results are visible."
    except Exception as e: return f"Search failed: {str(e)}"

def get_results_tool(start_index: int = 1, end_index: int = 10):
    """Extracts search results."""
    if not state.page: return "Error: Browser not connected."
    try:
        return search_extract_xplore(state.page, start_index, end_index)
    except Exception as e: return f"Extraction failed: {str(e)}"

def go_to_page_tool(page_number: int):
    """Navigates to a specific results page."""
    if not state.page: return "Error: Browser not connected."
    try:
        return navigate_to_page_xplore(state.page, page_number)
    except Exception as e: return f"Navigation failed: {str(e)}"

def open_document_tool(result_index: int):
    """Opens a document in a new tab."""
    if not state.page: return "Error: Browser not connected."
    try:
        new_page, info = document_page_xplore(state.page, result_index)
        state.page = new_page
        return f"Opened document in new tab.\n{info}"
    except Exception as e: return f"Failed to open document: {str(e)}"

def download_paper_tool():
    """Downloads the PDF of the current paper."""
    if not state.page: return "Error: Browser not connected."
    try:
        return document_download_xplore(state.page)
    except Exception as e: return f"Download failed: {str(e)}"

def list_tabs_tool():
    """Lists all open tabs with their titles and URLs."""
    if not state.context: return "Error: Browser not connected."
    try:
        pages = state.context.pages
        info = []
        for i, p in enumerate(pages):
            active_marker = "*" if p == state.page else " "
            info.append(f"{active_marker} [{i}] {p.title()} ({p.url})")
        return "\n".join(info)
    except Exception as e: return f"Failed to list tabs: {str(e)}"

def switch_tab_tool(index: int):
    """Switches focus to a specific tab index."""
    if not state.context: return "Error: Browser not connected."
    try:
        pages = state.context.pages
        if 0 <= index < len(pages):
            state.page = pages[index]
            state.page.bring_to_front()
            return f"Switched to tab {index}: {state.page.title()}"
        else:
            return f"Error: Invalid tab index {index}. Max index is {len(pages)-1}."
    except Exception as e: return f"Failed to switch tab: {str(e)}"

def close_tab_tool(index: int):
    """Closes a specific tab index."""
    if not state.context: return "Error: Browser not connected."
    try:
        pages = state.context.pages
        if 0 <= index < len(pages):
            page_to_close = pages[index]
            title = page_to_close.title()
            page_to_close.close()
            
            # Update state.page if we closed the active one
            if page_to_close == state.page:
                # Try to switch to the last available tab
                if state.context.pages:
                    state.page = state.context.pages[-1]
                    state.page.bring_to_front()
                else:
                    state.page = None
            
            return f"Closed tab {index}: {title}"
        else:
            return f"Error: Invalid tab index {index}."
    except Exception as e: return f"Failed to close tab: {str(e)}"

# --- Tool Definitions (JSON Schema) ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "launch_browser",
            "description": "Connects to the user's Chrome browser. Call this FIRST.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Searches for academic papers on IEEE Xplore.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keywords (e.g., 'LLM Agents')"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_results",
            "description": "Extracts a list of papers from the current page. RESTRICTION: Only works on Search Results pages.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_index": {"type": "integer", "description": "Start rank (default 1)"},
                    "end_index": {"type": "integer", "description": "End rank (default 10)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "go_to_page",
            "description": "Navigates to a specific page of search results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page_number": {"type": "integer", "description": "Page number to navigate to"}
                },
                "required": ["page_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_document",
            "description": "Opens a paper in a NEW tab. You must switch to the new tab to read/download it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "result_index": {"type": "integer", "description": "The index of the paper in the search results (1-based)"}
                },
                "required": ["result_index"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "download_paper",
            "description": "Downloads the PDF. RESTRICTION: Only works on Document Detail pages (not search results).",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tabs",
            "description": "Lists all open browser tabs. Use this to find valid indices for switching/closing.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "switch_tab",
            "description": "Switches focus to a tab. Tabs are 0-indexed. Use list_tabs() to check valid indices.",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer", "description": "The index of the tab to switch to (0-based)"}
                },
                "required": ["index"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_tab",
            "description": "Closes a tab. ADVICE: Close document tabs after downloading or if irrelevant to keep browser clean.",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer", "description": "The index of the tab to close (0-based)"}
                },
                "required": ["index"]
            }
        }
    }
]

available_functions = {
    "launch_browser": launch_browser_tool,
    "search": search_tool,
    "get_results": get_results_tool,
    "go_to_page": go_to_page_tool,
    "open_document": open_document_tool,
    "download_paper": download_paper_tool,
    "list_tabs": list_tabs_tool,
    "switch_tab": switch_tab_tool,
    "close_tab": close_tab_tool
}

# --- Main Agent Loop ---
def main():
    client = OpenAI(api_key=config.DEEPSEEK_API_KEY, base_url=BASE_URL)
    
    print(f"--- DeepSeek IEEE Xplore Agent ({MODEL_NAME}) ---")
    print("Type 'exit' to quit.")

    messages = [
        {"role": "system", "content": """You are an autonomous research assistant capable of using a web browser to find and download academic papers from IEEE Xplore.
        
        1. ALWAYS start by calling `launch_browser` to connect to the user's browser.
        2. Use `search` to find papers based on the user's request.
        3. If the user wants to download a paper, you might need to navigate to it manually (the user might be doing this, or you can assume the search results are there). 
           Currently, you can only download if you are on the paper's page or if there is a PDF button visible.
           
        The browser is ALREADY logged in as the user. Do not attempt to login.
        """}
    ]

    while True:
        try:
            user_input = input("\nUser: ")
        except EOFError:
            break

        if user_input.lower() in ["exit", "quit"]:
            break
            
        messages.append({"role": "user", "content": user_input})

        # Agent Loop
        while True:
            # 1. Get model response
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto"
                )
            except Exception as e:
                print(f"API Error: {e}")
                break
            
            msg = response.choices[0].message
            
            # Print Reasoning (Thinking Process)
            if hasattr(msg, 'reasoning_content') and msg.reasoning_content:
                print(f"\n🤔 Thought:\n{msg.reasoning_content}\n")
            
            # 2. Handle tool calls
            if msg.tool_calls:
                messages.append(msg) # Add assistant message with tool calls
                
                for tool_call in msg.tool_calls:
                    func_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    print(f"🛠️  Calling tool: {func_name}({args})")
                    
                    function_to_call = available_functions.get(func_name)
                    if function_to_call:
                        result = function_to_call(**args)
                    else:
                        result = f"Error: Function {func_name} not found"
                    
                    # Show full output
                    print(f"   -> Result: {str(result)}")
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(result)
                    })
            else:
                # No tool calls, just a text response. We are done with this turn.
                print(f"\n💬 Response: {msg.content}")
                messages.append(msg)
                break

if __name__ == "__main__":
    main()
