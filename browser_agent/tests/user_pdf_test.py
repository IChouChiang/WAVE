"""
User Browser PDF Download Test

This script connects to the running "Bot Browser" (port 9223) and attempts to 
download a PDF from IEEE Xplore to verify that the login session is active.
"""
import sys
import os
import time
from playwright.sync_api import sync_playwright

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the new user browser utility
from user_browser_utils import launch_user_browser
from config import settings as config

def main():
    print("============================================================")
    print("USER BROWSER PDF DOWNLOAD TEST")
    print("============================================================")
    print("1. Ensure 'launch_debug_chrome.ps1' is running.")
    print("2. Ensure you are LOGGED IN to IEEE Xplore in that window.")
    print("============================================================")
    
    with sync_playwright() as p:
        try:
            # Connect to the existing browser
            context, page = launch_user_browser(p, headless=False)
            
            # Target Paper (same as previous test)
            # "Specification and Evaluation of Multi-Agent LLM Systems"
            paper_url = "https://ieeexplore.ieee.org/document/11233474/"
            
            print(f"Navigating to paper: {paper_url}")
            page.goto(paper_url)
            page.wait_for_load_state("domcontentloaded")
            
            # Check for login indicator (simple check)
            # Usually "Sign Out" or user name is visible if logged in
            print("Checking page content...")
            page_content = page.content()
            if "Sign Out" in page_content or "My Settings" in page_content:
                print("✅ Login detected (found 'Sign Out' or 'My Settings').")
            else:
                print("⚠️  Warning: Could not definitively confirm login status from text.")
            
            # Attempt to find the PDF link/button
            print("Looking for PDF download options...")
            
            # Try the JS fetch method (stealthiest)
            print("Attempting to fetch PDF via page context (fetch API)...")
            
            # This script finds the PDF iframe or link and fetches it
            # We'll use a simplified version of the logic in xplore_actions.py
            
            # 1. Go to the stamp URL (PDF wrapper)
            stamp_url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=11233474"
            print(f"Navigating to PDF wrapper: {stamp_url}")
            page.goto(stamp_url)
            page.wait_for_load_state("networkidle")
            
            # 2. Find the iframe
            iframe = page.locator("iframe[src*='getPDF.jsp']").first
            if iframe.is_visible(timeout=5000):
                pdf_src = iframe.get_attribute("src")
                print(f"Found PDF iframe: {pdf_src}")
                
                if pdf_src and pdf_src.startswith("/"):
                    pdf_src = f"https://ieeexplore.ieee.org{pdf_src}"
                
                # 3. Fetch the blob
                print("Fetching PDF blob...")
                pdf_data_b64 = page.evaluate(f"""
                    async () => {{
                        const response = await fetch('{pdf_src}');
                        if (!response.ok) throw new Error('Fetch failed: ' + response.status);
                        const blob = await response.blob();
                        return new Promise((resolve, reject) => {{
                            const reader = new FileReader();
                            reader.onloadend = () => resolve(reader.result.split(',')[1]);
                            reader.onerror = reject;
                            reader.readAsDataURL(blob);
                        }});
                    }}
                """)
                
                # 4. Save to disk
                import base64
                pdf_bytes = base64.b64decode(pdf_data_b64)
                
                output_dir = config.PROJECT_ROOT / "downloads"
                if not output_dir.exists():
                    output_dir.mkdir(parents=True)
                    
                output_path = output_dir / "User_Profile_Test_Paper.pdf"
                
                with open(output_path, "wb") as f:
                    f.write(pdf_bytes)
                    
                print(f"✅ SUCCESS: PDF saved to {output_path}")
                print(f"   Size: {len(pdf_bytes) / 1024:.2f} KB")
                
            else:
                print("❌ Could not find PDF iframe. Are you sure you have access?")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
