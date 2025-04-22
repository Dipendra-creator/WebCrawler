#!/usr/bin/env python3
"""
Advanced example of web crawling with Playwright using proxies and user agents.
This example demonstrates how to use the utility functions for rotating proxies
and user agents for increased anonymity and avoiding blocks.
"""

import sys
import os
import json
import argparse
import logging
from typing import Dict, List, Optional

# Add the parent directory to the path so we can import the webcrawler package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webcrawler.crawler import Crawler
from webcrawler.utils import get_random_user_agent, load_proxies, is_robots_allowed


class AdvancedCrawler(Crawler):
    """
    Advanced crawler with proxy rotation and customized behavior.
    """
    
    def __init__(self, 
                 proxy_file: Optional[str] = None, 
                 user_agent_file: Optional[str] = None,
                 respect_robots_txt: bool = True,
                 **kwargs):
        """
        Initialize the advanced crawler.
        
        Args:
            proxy_file: Path to a JSON file containing proxy configurations
            user_agent_file: Path to a file containing user agents (one per line)
            respect_robots_txt: Whether to respect robots.txt rules
            **kwargs: Additional arguments passed to the base Crawler
        """
        self.proxy_file = proxy_file
        self.user_agent_file = user_agent_file
        self.respect_robots_txt = respect_robots_txt
        self.proxies = []
        
        # Load proxies if a file is provided
        if proxy_file and os.path.exists(proxy_file):
            self.proxies = load_proxies(proxy_file)
            # Use the first proxy initially or None if the list is empty
            initial_proxy = self.proxies[0] if self.proxies else None
        else:
            initial_proxy = None
            
        # Get a random user agent
        user_agent = get_random_user_agent(user_agent_file)
        
        # Initialize the base crawler
        super().__init__(
            proxy=initial_proxy,
            user_agent=user_agent,
            **kwargs
        )
        
        # Create a proxy rotation counter
        self.proxy_rotation_counter = 0
        
        logger.info(f"Initialized AdvancedCrawler with {len(self.proxies)} proxies and custom user agent")
    
    def crawl_page(self, page, url, depth=0):
        """
        Override crawl_page to implement robots.txt checking.
        
        Args:
            page: Playwright page object
            url: URL to crawl
            depth: Current depth level
            
        Returns:
            List of discovered URLs to crawl next
        """
        # Check robots.txt if enabled
        if self.respect_robots_txt and not is_robots_allowed(url, self.user_agent):
            logger.info(f"Skipping {url} - disallowed by robots.txt")
            return []
        
        # Rotate proxy after every 10 requests
        if self.proxies and self.proxy_rotation_counter >= 10:
            self._rotate_proxy(page)
            self.proxy_rotation_counter = 0
        
        # Increment the counter
        self.proxy_rotation_counter += 1
        
        # Call the parent method to handle the actual crawling
        return super().crawl_page(page, url, depth)
    
    def _rotate_proxy(self, page):
        """
        Rotate to a new proxy and user agent.
        
        Args:
            page: Current Playwright page object
        """
        # Close the current context
        context = page.context
        browser = context.browser
        
        # Get a new proxy from the list (cycling through them)
        proxy_index = (self.proxies.index(self.proxy) + 1) % len(self.proxies) if self.proxy in self.proxies else 0
        self.proxy = self.proxies[proxy_index]
        
        # Get a new user agent
        self.user_agent = get_random_user_agent(self.user_agent_file)
        
        logger.info(f"Rotating proxy to {self.proxy['server']} and new user agent")
        
        # Create a new context with the new proxy and user agent
        context_options = {'user_agent': self.user_agent}
        if self.proxy:
            context_options['proxy'] = self.proxy
            
        new_context = browser.new_context(**context_options)
        new_page = new_context.new_page()
        
        # Close the old context and replace references
        context.close()
        page = new_page


def create_example_proxy_file(filepath):
    """Create an example proxy file for demonstration."""
    example_proxies = [
        {
            "server": "http://proxy1.example.com:8080",
            "username": "user1",
            "password": "pass1"
        },
        {
            "server": "http://proxy2.example.com:8080"
        },
        {
            "server": "socks5://proxy3.example.com:1080",
            "username": "user3",
            "password": "pass3"
        }
    ]
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(example_proxies, f, indent=2)
    
    print(f"Created example proxy file at {filepath}")


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Advanced web crawler example")
    parser.add_argument("url", help="Starting URL to crawl")
    parser.add_argument("--max-depth", type=int, default=3, help="Maximum crawl depth")
    parser.add_argument("--max-pages", type=int, default=50, help="Maximum pages to crawl")
    parser.add_argument("--proxy-file", help="Path to proxy file (JSON format)")
    parser.add_argument("--user-agent-file", help="Path to user agent file (one per line)")
    parser.add_argument("--output-dir", default="advanced_crawl_results", help="Output directory")
    parser.add_argument("--browser", choices=["chromium", "firefox", "webkit"], default="chromium", help="Browser to use")
    parser.add_argument("--interval", type=float, default=2.0, help="Interval between requests in seconds")
    parser.add_argument("--create-proxy-example", action="store_true", help="Create an example proxy file and exit")
    
    return parser.parse_args()


def main():
    """Main function to run the advanced crawler example."""
    args = parse_arguments()
    
    # Create an example proxy file if requested
    if args.create_proxy_example:
        example_path = os.path.join(os.path.dirname(__file__), "example_proxies.json")
        create_example_proxy_file(example_path)
        return
    
    # Create and configure the crawler
    crawler = AdvancedCrawler(
        proxy_file=args.proxy_file,
        user_agent_file=args.user_agent_file,
        headless=True,
        max_depth=args.max_depth,
        max_pages=args.max_pages,
        request_interval=args.interval,
        browser_type=args.browser,
        output_dir=args.output_dir,
        respect_robots_txt=True
    )
    
    # Start the crawl
    print(f"Starting advanced crawl at {args.url}")
    print(f"Using browser: {args.browser}, max depth: {args.max_depth}, max pages: {args.max_pages}")
    
    if crawler.proxies:
        print(f"Using {len(crawler.proxies)} proxies with rotation")
    
    # Run the crawler
    data = crawler.crawl(args.url)
    
    # Print summary
    print(f"Crawl completed. Visited {len(crawler.visited_urls)} pages.")
    print(f"Data saved to {crawler.output_dir} directory.")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("AdvancedCrawler")
    
    main() 