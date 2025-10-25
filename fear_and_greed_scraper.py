from playwright.async_api import async_playwright
import asyncio
import random

def _get_user_agent() -> str:
    """Get a Chrome User-Agent to avoid blocking."""
    return "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"

async def capture_fear_greed_gauge():
    """
    Scrapes CNN Fear & Greed page using Playwright, finds the div with class 'market-tabbed-container', and screenshots it as PNG.
    """
    url = "https://edition.cnn.com/markets/fear-and-greed"
    
    try:
        async with async_playwright() as p:
            print("Launching browser...")
            browser = await p.firefox.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            print("Browser launched, creating context...")
            context = await browser.new_context(
                user_agent=_get_user_agent(),
                viewport={'width': 1200, 'height': 800}
            )
            page = await context.new_page()
            await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            await page.set_extra_http_headers({"User-Agent": _get_user_agent()})
            print("Going to URL...")
            await page.goto(url)
            print("Waiting for load state...")
            await page.wait_for_load_state('domcontentloaded')
            print("Waiting for selector...")
            await page.wait_for_selector('.market-tabbed-container', timeout=10000)
            print("Selector found, waiting for content...")
            await page.wait_for_timeout(3000)  # Wait for dynamic content
            print("Taking screenshot...")
            #take a screen shot of the div with class 'market-tabbed-container', select a div
            div_handle = await page.query_selector('.market-tabbed-container')
            if div_handle:
                await div_handle.scroll_into_view_if_needed()
                await page.wait_for_timeout(2000)  # Wait after scroll
                screenshot_bytes = await div_handle.screenshot()
                print("Captured div screenshot.")
            else:
                print("Selector not found, cannot take screenshot.")
                screenshot_bytes = None
            print("Screenshot taken.")
            
            await browser.close()
        
        print("Div scraped successfully.")
        return screenshot_bytes
    except Exception as e:
        print(f"Error in scraper: {e}")
        return None

if __name__ == "__main__":
    asyncio.run(capture_fear_greed_gauge())
