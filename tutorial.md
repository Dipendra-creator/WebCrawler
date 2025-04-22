# Playwright Web Crawler Tutorial

This tutorial demonstrates how to use the Playwright Web Crawler to extract data from websites.

## Installation

1. First, install the required Python packages:

```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:

```bash
playwright install
```

## Basic Usage

The simplest way to use the crawler is with the default settings:

```python
from webcrawler.crawler import Crawler

# Create a crawler with default settings
crawler = Crawler()

# Start crawling from a URL
data = crawler.crawl("https://example.com")

# The data is automatically saved to the 'output' directory
# You can also access it directly from the 'data' variable
print(f"Crawled {len(data)} pages")
```

## Customizing the Crawler

You can customize the crawler by passing parameters:

```python
crawler = Crawler(
    headless=True,           # Run in headless mode (no browser UI)
    max_depth=3,             # Maximum link depth to crawl
    max_pages=100,           # Maximum number of pages to crawl
    request_interval=1.5,    # Wait time between requests (seconds)
    browser_type="chromium", # Browser to use (chromium, firefox, webkit)
    output_dir="my_results"  # Directory to save results
)
```

## Running the Examples

The project includes several examples to get you started:

### Simple Crawl

```bash
python examples/simple_crawl.py
```

This will crawl `example.com` with basic settings.

### Custom Extractor

```bash
python examples/custom_extractor.py
```

This demonstrates how to create a custom crawler that extracts specific data (product information) from pages.

### Advanced Crawl

```bash
python examples/advanced_crawl.py https://example.com --max-depth 2 --max-pages 20
```

The advanced example supports:
- Proxy rotation
- User agent rotation
- Respecting robots.txt
- Command-line arguments

To create an example proxy file:

```bash
python examples/advanced_crawl.py --create-proxy-example
```

Then use it:

```bash
python examples/advanced_crawl.py https://example.com --proxy-file examples/example_proxies.json
```

## Creating Your Own Crawler

To create a custom crawler for specific data extraction needs:

1. Subclass the `Crawler` class
2. Override the `extract_data` method
3. Optionally, override `extract_links` to customize link extraction

Example:

```python
from webcrawler.crawler import Crawler
from playwright.sync_api import Page

class MyCrawler(Crawler):
    def extract_data(self, page: Page):
        """Custom data extraction logic"""
        title = page.title()
        url = page.url
        
        # Extract specific elements using CSS selectors
        main_content = page.text_content("#main-content")
        
        return {
            "url": url,
            "title": title,
            "main_content": main_content,
            # Add any other data you want to extract
        }
```

## Best Practices

1. **Be Respectful**: Set appropriate delays between requests (1-3 seconds)
2. **Identify Your Bot**: Use a descriptive user agent
3. **Respect robots.txt**: Use the AdvancedCrawler with `respect_robots_txt=True`
4. **Use Proxies** for large-scale crawling to avoid IP bans
5. **Handle Errors** gracefully to ensure your crawler continues working

## Troubleshooting

- **Slow Performance**: Try using a different browser (firefox or webkit)
- **Blocked by Website**: Use proxy rotation and random user agents
- **Memory Issues**: Lower the `max_pages` setting
- **Playwright Errors**: Ensure your Playwright installation is complete with `playwright install`

## Advanced Features

- **Authentication**: Use `context.browser_context.add_cookies()` to add login cookies
- **JavaScript Heavy Sites**: Increase the wait time with `page.wait_for_timeout()`
- **Custom Headers**: Set headers using the BrowserContext
- **Dynamic Content**: Use `page.wait_for_selector()` to wait for specific elements

For more information, refer to the [Playwright Python documentation](https://playwright.dev/python/docs/intro). 