from playwright.sync_api import sync_playwright


def scrape_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle')
        content = page.content()
        browser.close()
    return content


def extract_titles_and_links(content):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    titles = [h2.get_text(strip=True) for h2 in soup.find_all('h2')]
    links = [a.get('href') for a in soup.find_all('a') if a.get('href') and a.get('href').startswith('http')]
    return titles, links


if __name__ == "__main__":
    url = "https://dipendra-bhardwaj.vercel.app/"
    content = scrape_with_playwright(url)
    titles, links = extract_titles_and_links(content)
    for idx, title in enumerate(titles, start=1):
        print(f"{idx}. {title}")
    print("Links:")
    for link in links:
        print(link)
