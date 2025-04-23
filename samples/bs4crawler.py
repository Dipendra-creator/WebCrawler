import requests
from bs4 import BeautifulSoup

def fetch_titles(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()  # blow up if status != 200

    soup = BeautifulSoup(resp.text, 'html.parser')

    titles = [h2.get_text(strip=True) for h2 in soup.find_all('h2')]
    links = [a.get('href') for a in soup.find_all('a') if a.get('href') and a.get('href').startswith('http')]
    return links

if __name__ == "__main__":
    url = "https://dipendra-bhardwaj.vercel.app/"
    for idx, title in enumerate(fetch_titles(url), start=1):
        print(f"{idx}. {title}")
