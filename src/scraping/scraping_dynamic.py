from playwright.async_api import async_playwright

async def render_dynamic_page(url, selector: str):
    async with async_playwright() as p:
        browser = None # Initialize browser to None
        try:
            # Launch the headless browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Navigate to the UR
            print(f"Navigating to {url}...")
            await page.goto(url)

            # Wait for the key element to appear.
            if selector:
                print(f"Waitinf for selector: {selector}")
                await page.wait_for_selector(selector, timeout=10000)
            else:# Fallback to waiting for the DOM if no selector is provided
                print("No specific selector provided. Waiting for 'domcontentloaded'...")
                await page.wait_for_load_state('networkidle')

            # Get the rendered HTML content
            print("Element found. Getting HTMl content...")
            html_content = await page.content()

            return html_content
        except Exception as e:
            print(f"Error redering dynamic page: {e}")
            return None
        finally:
            # Ensure the browser is always closed, even if an error occurs.
            if 'browser' in locals() and browser.is_connected():
                await browser.close()
        
    