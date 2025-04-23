from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import random

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Mobile Safari/537.36"
]
PROXIES = [
# {"server": "198.49.68.80:80", "username": "", "password": ""},
# {"server": "18.134.236.231:1080", "username": "", "password": ""},
# {"server": "170.106.193.157:13001", "username": "", "password": ""}
]



def scrape_with_playwright(url, idx):
    proxy = PROXIES[idx]
    user_agent = random.choice(USER_AGENTS)

    with sync_playwright() as p:
        browser = p.chromium.launch(proxy=proxy)
        page = browser.new_page()
        page.set_extra_http_headers({"USER-AGENT": user_agent})
        stealth_sync(page)
        page.goto(url, wait_until='networkidle')
        content = page.content()
        browser.close()
    return content

if __name__ == "__main__":
    for i in range(len(PROXIES)):
        url = "https://httpbin.org/ip"
        try:
            content = scrape_with_playwright(url, i)
            print(content)

        except Exception as e:
            pass
