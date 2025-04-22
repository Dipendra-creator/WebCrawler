# Web Crawler Guide

## Introduction

This guide explains how the `crawler.py` module works, providing a detailed walkthrough of its features, architecture, and usage. The crawler is built using Playwright for browser automation and provides a robust, configurable solution for web crawling needs.

## Overview

The web crawler is designed to:
- Navigate web pages programmatically using a headless browser
- Extract data from visited pages
- Follow links to discover additional pages
- Respect depth and page count limits
- Save extracted data and screenshots

## Core Components

### Crawler Class

The main `Crawler` class handles the entire crawling process. It's initialized with several configurable parameters and maintains state during the crawling process.

```python
class Crawler:
    def __init__(self, 
                headless: bool = True,
                slow_mo: int = 0,
                user_agent: str = None,
                proxy: Optional[Dict[str, str]] = None,
                request_interval: float = 1.0,
                max_depth: int = 3,
                max_pages: int = 100,
                browser_type: str = 'chromium',
                output_dir: str = 'output'):
        # ...
```

### Key Data Structures

- `visited_urls`: A set containing all URLs that have been crawled
- `data`: A list of dictionaries containing extracted data from each page

## Key Methods

### 1. `_get_browser_context()`

This method configures and initializes the Playwright browser:

```python
def _get_browser_context(self) -> tuple[Browser, BrowserContext]:
    """Create and configure browser and context."""
    playwright = sync_playwright().start()
    
    # Initialize browser based on type
    if self.browser_type == 'firefox':
        browser = playwright.firefox.launch(headless=self.headless, slow_mo=self.slow_mo)
    elif self.browser_type == 'webkit':
        browser = playwright.webkit.launch(headless=self.headless, slow_mo=self.slow_mo)
    else:
        browser = playwright.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)
    
    # Configure browser context
    context_options = {}
    if self.user_agent:
        context_options['user_agent'] = self.user_agent
    if self.proxy:
        context_options['proxy'] = self.proxy
        
    context = browser.new_context(**context_options)
    return browser, context
```

### 2. `extract_data()`

Extracts data from the currently loaded web page:

```python
def extract_data(self, page: Page) -> Dict[str, Any]:
    """
    Extract data from the current page. Override this method for custom extraction.
    """
    # Basic extraction (override this method for custom extraction)
    title = page.title()
    url = page.url
    
    # Example extraction of text content
    body_text = page.evaluate('() => document.body.innerText')
    
    # Example extraction of meta tags
    meta_tags = page.evaluate('''() => {
        const metaTags = {};
        document.querySelectorAll('meta').forEach(meta => {
            if (meta.name) metaTags[meta.name] = meta.content;
            else if (meta.property) metaTags[meta.property] = meta.content;
        });
        return metaTags;
    }''')
    
    return {
        'url': url,
        'title': title,
        'timestamp': datetime.now().isoformat(),
        'body_text': body_text[:1000] + "..." if len(body_text) > 1000 else body_text,
        'meta_tags': meta_tags
    }
```

### 3. `extract_links()`

Finds and processes links from the current page:

```python
def extract_links(self, page: Page, base_url: str) -> List[str]:
    """
    Extract links from the current page.
    """
    # Get all links on the page
    links = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('a[href]'))
            .map(a => a.href)
            .filter(href => href && !href.startsWith('javascript:') && !href.startsWith('mailto:'));
    }''')
    
    # Process and filter links
    parsed_base = urlparse(base_url)
    filtered_links = []
    
    for link in links:
        # Resolve relative URLs
        absolute_url = urljoin(base_url, link)
        parsed = urlparse(absolute_url)
        
        # Only include links from the same domain
        if parsed.netloc == parsed_base.netloc:
            # Normalize the URL (remove fragments)
            normalized_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if parsed.query:
                normalized_url += f"?{parsed.query}"
            
            filtered_links.append(normalized_url)
    
    return list(set(filtered_links))  # Remove duplicates
```

### 4. `crawl_page()`

Handles the crawling of a single page:

```python
def crawl_page(self, page: Page, url: str, depth: int = 0) -> List[str]:
    """
    Crawl a single page and extract data and links.
    """
    if url in self.visited_urls:
        return []
    
    if len(self.visited_urls) >= self.max_pages:
        return []
        
    if depth > self.max_depth:
        return []
    
    # Mark as visited before navigate to avoid revisiting on errors
    self.visited_urls.add(url)
    
    try:
        # Navigate to the URL
        logger.info(f"Crawling: {url} (depth: {depth})")
        page.goto(url, wait_until="domcontentloaded")
        
        # Wait a bit for any dynamic content to load
        page.wait_for_timeout(1000)
        
        # Extract data from the page
        data = self.extract_data(page)
        self.data.append(data)
        
        # Save screenshot
        screenshots_dir = os.path.join(self.output_dir, 'screenshots')
        os.makedirs(screenshots_dir, exist_ok=True)
        page.screenshot(path=os.path.join(screenshots_dir, f"{len(self.visited_urls)}.png"))
        
        # Extract links for further crawling
        if depth < self.max_depth:
            links = self.extract_links(page, url)
            # Only return links we haven't visited yet
            return [link for link in links if link not in self.visited_urls]
        
    except Exception as e:
        logger.error(f"Error crawling {url}: {str(e)}")
    
    # Add delay between requests to be respectful
    time.sleep(self.request_interval)
    return []
```

### 5. `crawl()`

The main method that starts the crawling process:

```python
def crawl(self, start_url: str) -> List[Dict[str, Any]]:
    """
    Start crawling from a given URL.
    """
    browser, context = self._get_browser_context()
    page = context.new_page()
    
    try:
        # BFS (Breadth-First Search) crawling
        urls_to_crawl = [start_url]
        current_depth = 0
        
        with tqdm(total=self.max_pages, desc="Crawling") as pbar:
            while urls_to_crawl and len(self.visited_urls) < self.max_pages:
                # Get the next URLs to process at this depth
                current_urls = urls_to_crawl
                urls_to_crawl = []
                
                # Process all URLs at the current depth
                for url in current_urls:
                    if url in self.visited_urls or len(self.visited_urls) >= self.max_pages:
                        continue
                        
                    # Crawl the page and collect new URLs
                    new_urls = self.crawl_page(page, url, current_depth)
                    urls_to_crawl.extend(new_urls)
                    
                    # Update progress bar
                    pbar.update(1)
                
                # Move to the next depth level
                current_depth += 1
                if current_depth > self.max_depth:
                    break
        
        # Save the crawled data
        self.save_data()
        
        return self.data
        
    finally:
        # Clean up resources
        page.close()
        context.close()
        browser.close()
```

### 6. `save_data()`

Saves the collected data to a JSON file:

```python
def save_data(self) -> None:
    """Save the crawled data to disk."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(self.output_dir, f"crawl_data_{timestamp}.json")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'urls_crawled': len(self.visited_urls),
                'max_depth': self.max_depth,
                'timestamp': datetime.now().isoformat()
            },
            'data': self.data
        }, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Saved {len(self.data)} crawled pages to {filename}")
```

## Crawling Process Flow

The crawler follows these steps to process web pages:

1. **Initialization**: The crawler is created with configuration parameters.
2. **Browser Setup**: Playwright browser is launched with the specified settings.
3. **Breadth-First Search**: The crawler uses BFS to explore pages by depth level.
4. **Page Processing**:
   - Navigate to the URL
   - Extract data from the page
   - Take a screenshot
   - Extract links for further crawling
5. **Data Storage**: All extracted data is saved to a JSON file.
6. **Resource Cleanup**: Browser and page resources are properly closed.

## Usage Examples

### Basic Usage

```python
from webcrawler.crawler import Crawler

# Create a crawler instance
crawler = Crawler(
    headless=True,
    max_depth=2,
    max_pages=50,
    output_dir='crawl_results'
)

# Start crawling from a URL
data = crawler.crawl('https://example.com')

# Data is also saved automatically to the output directory
```

### Custom Data Extraction

You can extend the Crawler class to customize data extraction:

```python
class CustomCrawler(Crawler):
    def extract_data(self, page):
        # Get basic data from parent method
        data = super().extract_data(page)
        
        # Add custom extraction
        data['product_prices'] = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('.product-price'))
                .map(el => el.innerText);
        }''')
        
        return data
```

## Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `headless` | bool | `True` | Whether to run browser in headless mode |
| `slow_mo` | int | `0` | Slow down operations by specified milliseconds |
| `user_agent` | str | `None` | Custom user agent string |
| `proxy` | Dict | `None` | Proxy configuration |
| `request_interval` | float | `1.0` | Time to wait between requests in seconds |
| `max_depth` | int | `3` | Maximum link depth to crawl |
| `max_pages` | int | `100` | Maximum number of pages to crawl |
| `browser_type` | str | `'chromium'` | Browser to use (chromium, firefox, webkit) |
| `output_dir` | str | `'output'` | Directory to save crawled data |

## Best Practices

1. **Be Respectful**: Set appropriate `request_interval` to avoid overloading websites.
2. **Use Headless Mode**: For production, keep `headless=True` for better performance.
3. **Limit Depth and Pages**: Use reasonable values for `max_depth` and `max_pages`.
4. **Custom User Agent**: Set a descriptive user agent to identify your crawler.
5. **Error Handling**: Monitor the crawler logs for errors and fix them.
6. **Data Processing**: Process the data after crawling, rather than during crawling for better performance.

## Extending the Crawler

The crawler is designed to be extended. Common extension points include:

1. **Custom Data Extraction**: Override the `extract_data` method.
2. **Link Filtering**: Modify the `extract_links` method to implement custom link filtering.
3. **Screenshot Processing**: Add post-processing for screenshots.
4. **Advanced Analysis**: Add methods to analyze the crawled data.

## Conclusion

This web crawler provides a solid foundation for web scraping and data extraction projects. It combines the power of Playwright's browser automation with a structured, configurable approach to crawling. By understanding its components and operation, you can adapt it to your specific needs or use it as-is for general-purpose web crawling. 