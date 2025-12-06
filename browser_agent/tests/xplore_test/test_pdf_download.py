import sys
import os
import time
from playwright.sync_api import sync_playwright

# Add browser_agent directory to path so we can import modules
# File is in browser_agent/tests/xplore_test/test_pdf_download.py
# We want to add browser_agent/ to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
browser_agent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(browser_agent_dir)

try:
    from browser_utils import launch_persistent_browser
    from xplore_actions import search_xplore, document_page_xplore, document_download_xplore
    from config import settings as config
except ImportError as e:
    print(f"Import Error: {e}")
    print(f"Current sys.path: {sys.path}")
    sys.exit(1)

def test_pdf_download():
    print("Starting PDF download test...")
    
    with sync_playwright() as p:
        # Launch browser (headless=False to see what's happening)
        context, page = launch_persistent_browser(p, headless=False)
        
        # Navigate to IEEE Xplore
        print("Navigating to IEEE Xplore...")
        page.goto("https://ieeexplore.ieee.org/Xplore/home.jsp")
        
        # Wait for manual sign-in
        print("\n" + "="*60)
        print("WAITING FOR MANUAL SIGN-IN")
        print("1. Please sign in to IEEE Xplore in the browser window.")
        print("2. Ensure you have access rights to download PDFs.")
        print("3. Return to the home page or stay on a page where search bar is visible.")
        print("="*60 + "\n")
        
        while True:
            user_input = input("Have you signed in and are ready to continue? (Y/N): ").strip().upper()
            if user_input == 'Y':
                break
            print("Waiting for user confirmation...")
            time.sleep(1)
            
        print("Continuing with test...")
        
        # Search for a paper
        # Using "LLM agent" as a query, likely to have recent papers
        query = "LLM agent"
        search_xplore(page, query)
        
        # Open the first document
        print("Opening first document...")
        # document_page_xplore returns (new_page, info_string)
        # We use index 1 (first result)
        try:
            doc_page, doc_info = document_page_xplore(page, result_index=1)
            
            print(f"Document opened: {doc_page.url}")
            print("-" * 20)
            print(doc_info)
            print("-" * 20)
            
            # Try to download/open PDF
            print("Attempting to download/open PDF...")
            result = document_download_xplore(doc_page)
            print(f"Result: {result}")
            
        except Exception as e:
            print(f"Error during document interaction: {e}")
        
        print("\nTest complete. Browser will remain open for inspection.")
        input("Press Enter to close browser and exit...")

if __name__ == "__main__":
    test_pdf_download()
