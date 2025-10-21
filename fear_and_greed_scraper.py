from playwright.sync_api import sync_playwright
import random

def _get_user_agent() -> str:
    """Get a random User-Agent to avoid blocking."""
    user_agents = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:82.1) Gecko/20100101 Firefox/82.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:84.0) Gecko/20100101 Firefox/84.0",
    ]
    return random.choice(user_agents)

def capture_fear_greed_gauge():
    """
    Scrapes CNN Fear & Greed page using Playwright, finds the div with class 'market-tabbed-container', and screenshots it as PNG.
    """
    url = "https://money.cnn.com/data/fear-and-greed/"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1200, "height": 800})
        page.set_extra_http_headers({"User-Agent": _get_user_agent()})
        page.goto(url)
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(3000)  # Wait for dynamic content to load
        
        # Wait for the container div to load
        page.wait_for_selector('div.market-tabbed-container', timeout=10000)
        
        # Screenshot the container div
        element = page.locator('div.market-tabbed-container')
        screenshot_bytes = element.screenshot()
        
        browser.close()
    
    print("Div scraped successfully.")
    return screenshot_bytes

if __name__ == "__main__":
    capture_fear_greed_gauge()
