#!/usr/bin/env python3
"""
Simple example of using the Playwright web crawler.
"""

import sys
import os

# Add the parent directory to the path so we can import the webcrawler package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from webcrawler.crawler import Crawler

def main():
    # Create a crawler with custom settings
    crawler = Crawler(
        headless=True,           # Run in headless mode
        max_depth=2,             # Crawl up to 2 links deep
        max_pages=10,            # Crawl at most 10 pages
        request_interval=2.0,    # Wait 2 seconds between requests
        output_dir='crawl_results'
    )
    
    # Start crawling from a website
    url = "https://dipendra-bhardwaj.vercel.app/"
    print(f"Starting crawl at {url}")
    
    # Run the crawler
    data = crawler.crawl(url)
    
    # Print summary
    print(f"Crawl completed. Visited {len(crawler.visited_urls)} pages.")
    print(f"Data saved to {crawler.output_dir} directory.")

if __name__ == "__main__":
    main() 