import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def scrape_dynamic_page(url):
    async with async_playwright() as p:
        # Launch the headless browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to the URL and wait for the page to load
        print(f"Navigating to {url}...")
        await page.goto(url, wait_until="networkidle")

        # Get the rendered HTML content
        print("Page loaded. Getting HTML content...")
        html_content = await page.content()

        # Close the browser
        await browser.close()
        
    return html_content