import os
import sys
import json
import time
from typing import Optional
from openai import OpenAI
from playwright.sync_api import sync_playwright, Page, BrowserContext

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from browser_utils import launch_persistent_browser
from xhs_actions import search_xhs, extract_search_results, extract_post_details, close_post_details, apply_search_filters

# --- Configuration ---
# API Key is loaded from a local file to avoid hardcoding secrets.
API_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ds_api.txt")
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-reasoner"  # Using Thinking Mode (R1) for complex reasoning

# --- State Management ---
# Maintains the browser instance globally so it persists between LLM turns.
class BrowserState:
    playwright = None
    context: Optional[BrowserContext] = None
    page: Optional[Page] = None

state = BrowserState()

# --- Tool Implementations ---
# These functions wrap the core logic from xhs_actions.py and browser_utils.py
# to provide a clean interface for the LLM to call.

def launch_browser_tool():
    """Launches the persistent browser session."""
    if state.page:
        return "Browser is already running."
    try:
        state.playwright = sync_playwright().start()
        state.context, state.page = launch_persistent_browser(state.playwright, user_data_dir="./chrome_user_data")
        state.page.goto("https://www.xiaohongshu.com/explore")
        return "Browser launched successfully. You are on the Explore page."
    except Exception as e:
        return f"Failed to launch browser: {str(e)}"

def search_tool(query: str):
    """Searches for a keyword."""
    if not state.page: return "Error: Browser not running."
    try:
        search_xhs(state.page, query)
        return f"Search for '{query}' completed. Results are visible."
    except Exception as e: return f"Search failed: {str(e)}"

def filter_results_tool(category: str, option: str):
    """Applies a search filter."""
    if not state.page: return "Error: Browser not running."
    try:
        apply_search_filters(state.page, {category: option})
        return f"Applied filter: {category} = {option}"
    except Exception as e: return f"Filter failed: {str(e)}"

def get_results_list_tool(max_results: int = 10):
    """Gets the list of search results."""
    if not state.page: return "Error: Browser not running."
    try:
        return extract_search_results(state.page, max_results)
    except Exception as e: return f"Extraction failed: {str(e)}"

def open_post_tool(index: int):
    """Opens a post by index (0-based)."""
    if not state.page: return "Error: Browser not running."
    try:
        covers = state.page.locator(".cover").all()
        if index >= len(covers):
            return f"Error: Index {index} out of range. Only {len(covers)} posts found."
        
        target_cover = covers[index]
        target_cover.wait_for(state="visible", timeout=5000)
        target_cover.click()
        state.page.wait_for_selector("#noteContainer", timeout=10000)
        return f"Opened post at index {index}."
    except Exception as e: return f"Failed to open post: {str(e)}"

def get_post_details_tool():
    """Extracts details from the open post."""
    if not state.page: return "Error: Browser not running."
    try:
        return extract_post_details(state.page)
    except Exception as e: return f"Detail extraction failed: {str(e)}"

def close_post_tool():
    """Closes the post modal."""
    if not state.page: return "Error: Browser not running."
    try:
        close_post_details(state.page)
        return "Post closed."
    except Exception as e: return f"Failed to close post: {str(e)}"

# --- Tool Definitions (JSON Schema) ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "launch_browser",
            "description": "Launch the browser. MUST be called first.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Search XHS for a query.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Search keyword"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "filter_results",
            "description": "Apply search filters. You MUST use the EXACT option names listed in the description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string", "enum": ["排序依据", "笔记类型", "发布时间", "搜索范围", "位置距离"]},
                    "option": {
                        "type": "string", 
                        "description": "The filter option value. MUST be one of: ['综合', '最新', '最多点赞', '最多评论', '最多收藏'] for '排序依据'; ['不限', '视频', '图文'] for '笔记类型'; ['不限', '一天内', '一周内', '半年内'] for '发布时间'; ['不限', '已看过', '未看过', '已关注'] for '搜索范围'; ['不限', '同城', '附近'] for '位置距离'."
                    }
                },
                "required": ["category", "option"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_results_list",
            "description": "Get the list of search results (titles/likes).",
            "parameters": {
                "type": "object",
                "properties": {"max_results": {"type": "integer", "default": 10}},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_post",
            "description": "Open a post by index from the results list.",
            "parameters": {
                "type": "object",
                "properties": {"index": {"type": "integer"}},
                "required": ["index"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_post_details",
            "description": "Read the content/comments of the currently open post. IMPORTANT: Each time after using this tool, the close_post tool MUST be used once again to make sure to go back to the search result.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_post",
            "description": "Close the current post modal.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]

available_functions = {
    "launch_browser": launch_browser_tool,
    "search": search_tool,
    "filter_results": filter_results_tool,
    "get_results_list": get_results_list_tool,
    "open_post": open_post_tool,
    "get_post_details": get_post_details_tool,
    "close_post": close_post_tool,
}

# --- Main Agent Loop ---
def main():
    # 1. Load API Key
    try:
        with open(API_KEY_FILE, "r") as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        print(f"Error: API key file not found at {API_KEY_FILE}")
        return

    client = OpenAI(api_key=api_key, base_url=BASE_URL)
    
    print(f"--- DeepSeek XHS Agent ({MODEL_NAME}) ---")
    print("Type 'exit' to quit.")
    
    messages = [
        {"role": "system", "content": "You are an intelligent researcher agent for Xiaohongshu (XHS). Use the browser tools to find information, analyze posts, and summarize findings. Always launch the browser first. When researching, try to find high-quality posts (high likes) and read their comments for sentiment. IMPORTANT: After opening and reading a post, you MUST call close_post() before proceeding to the next one or finishing."}
    ]

    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        messages.append({"role": "user", "content": user_input})
        
        # Tool Loop
        while True:
            print("\n[DeepSeek Thinking...]")
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

            message = response.choices[0].message
            
            # Print Reasoning (Thinking Process)
            if hasattr(message, 'reasoning_content') and message.reasoning_content:
                print(f"\n[Thought Process]:\n{message.reasoning_content}\n")
            
            # If the model wants to call tools
            if message.tool_calls:
                # Append the assistant's message (with tool calls) to history
                messages.append(message)
                
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    print(f"[Executing Tool]: {function_name}({function_args})")
                    
                    function_to_call = available_functions.get(function_name)
                    if function_to_call:
                        tool_result = function_to_call(**function_args)
                    else:
                        tool_result = f"Error: Function {function_name} not found"
                    
                    print(f"[Tool Output]: {str(tool_result)[:200]}..." if len(str(tool_result)) > 200 else f"[Tool Output]: {tool_result}")
                    
                    # Append tool result to history
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": str(tool_result)
                    })
                # Loop continues to let the model process the tool output
            else:
                # Final answer (no more tools)
                print(f"\n[Assistant]: {message.content}")
                messages.append(message)
                break
                
    # Cleanup
    if state.context:
        state.context.close()
    if state.playwright:
        state.playwright.stop()

if __name__ == "__main__":
    main()
