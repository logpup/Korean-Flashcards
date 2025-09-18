import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def render_dynamic_page(url):
    async with async_playwright() as p:
        try:
            # Launch the headless browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Navigate to the URL and wait for the page to load
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="domcontentloaded")

            # Get the rendered HTML content
            print("Page loaded. Getting HTML content...")
            html_content = await page.content()

            return html_content
        except Exception as e:
            print(f"Error redering dynamic page: {e}")
            return None
        finally:
            # Ensure the browser is always closed, even if an error occurs.
            if 'browser' in locals() and browser.is_connected():
                await browser.close()
        
    