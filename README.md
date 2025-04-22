# Playwright Web Crawler

A Python web crawling system using Playwright for browser automation.

## Features

- Headless browser automation with Playwright
- Configurable crawling parameters
- Proxy support
- Rate limiting
- Data extraction and saving

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

3. Create a `.env` file (optional) for configuration:
```
HEADLESS=true
SLOW_MO=50
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
```

## Usage

Basic usage:
```python
from webcrawler.crawler import Crawler

crawler = Crawler()
data = crawler.crawl('https://example.com')
```

See `examples/` folder for more usage examples. 