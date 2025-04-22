import os
import time
import json
import logging
from typing import Dict, List, Any, Optional, Union, Set
from urllib.parse import urljoin, urlparse
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext
from tqdm import tqdm

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("crawler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PlaywrightCrawler")

class Crawler:
    """A web crawler using Playwright for browser automation."""
    
    def __init__(self, 
                 headless: bool = os.getenv('HEADLESS', 'true').lower() == 'true',
                 slow_mo: int = int(os.getenv('SLOW_MO', '0')),
                 user_agent: str = os.getenv('USER_AGENT', None),
                 proxy: Optional[Dict[str, str]] = None,
                 request_interval: float = 1.0,
                 max_depth: int = 3,
                 max_pages: int = 100,
                 browser_type: str = 'chromium',
                 output_dir: str = 'output'):
        """
        Initialize the crawler with configuration options.
        
        Args:
            headless: Whether to run browser in headless mode
            slow_mo: Slow down operations by specified milliseconds
            user_agent: Custom user agent string
            proxy: Proxy configuration dict
            request_interval: Time to wait between requests in seconds
            max_depth: Maximum link depth to crawl
            max_pages: Maximum number of pages to crawl
            browser_type: Browser to use (chromium, firefox, webkit)
            output_dir: Directory to save crawled data
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.user_agent = user_agent
        self.proxy = proxy
        self.request_interval = request_interval
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.browser_type = browser_type
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize collections
        self.visited_urls: Set[str] = set()
        self.data: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized crawler with max_depth={max_depth}, max_pages={max_pages}")
    
    def _get_browser_context(self) -> tuple[Browser, BrowserContext]:
        """Create and configure browser and context."""
        playwright = sync_playwright().start()
        
        if self.browser_type == 'firefox':
            browser = playwright.firefox.launch(headless=self.headless, slow_mo=self.slow_mo)
        elif self.browser_type == 'webkit':
            browser = playwright.webkit.launch(headless=self.headless, slow_mo=self.slow_mo)
        else:
            browser = playwright.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)
        
        context_options = {}
        if self.user_agent:
            context_options['user_agent'] = self.user_agent
        if self.proxy:
            context_options['proxy'] = self.proxy
            
        context = browser.new_context(**context_options)
        return browser, context
    
    def extract_data(self, page: Page) -> Dict[str, Any]:
        """
        Extract data from the current page. Override this method for custom extraction.
        
        Args:
            page: Playwright page object
            
        Returns:
            Dictionary of extracted data
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
            'body_text': body_text[:1000] + "..." if len(body_text) > 1000 else body_text,  # Truncate long text
            'meta_tags': meta_tags
        }
    
    def extract_links(self, page: Page, base_url: str) -> List[str]:
        """
        Extract links from the current page.
        
        Args:
            page: Playwright page object
            base_url: Base URL for resolving relative links
            
        Returns:
            List of extracted URLs
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
    
    def crawl_page(self, page: Page, url: str, depth: int = 0) -> List[str]:
        """
        Crawl a single page and extract data and links.
        
        Args:
            page: Playwright page object
            url: URL to crawl
            depth: Current depth level
            
        Returns:
            List of discovered URLs to crawl next
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
            
            # Save screenshot (optional)
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
    
    def crawl(self, start_url: str) -> List[Dict[str, Any]]:
        """
        Start crawling from a given URL.
        
        Args:
            start_url: The URL to start crawling from
            
        Returns:
            List of dictionaries containing extracted data
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