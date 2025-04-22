#!/usr/bin/env python3
"""
Example of creating a custom crawler by extending the base Crawler class.
This example extracts product information from a hypothetical e-commerce site.
"""

import sys
import os
from typing import Dict, Any, List

# Add the parent directory to the path so we can import the webcrawler package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import Page
from webcrawler.crawler import Crawler


class ProductCrawler(Crawler):
    """Custom crawler for extracting product information from an e-commerce site."""
    
    def extract_data(self, page: Page) -> Dict[str, Any]:
        """
        Override the extract_data method to extract specific product information.
        
        Args:
            page: Playwright page object
            
        Returns:
            Dictionary of extracted product data
        """
        # Get basic information
        url = page.url
        title = page.title()
        
        # Check if this is a product page (customize this selector for your target site)
        is_product_page = page.is_visible('.product-details', timeout=1000)
        
        if not is_product_page:
            # Not a product page, collect minimal data
            return {
                'url': url,
                'title': title,
                'is_product': False
            }
        
        # Extract product specific information using CSS selectors
        # (These selectors should be customized for the specific site you're crawling)
        try:
            product_name = page.text_content('.product-name')
            product_price = page.text_content('.product-price')
            
            # Extract product description (might contain HTML)
            product_description = page.inner_text('.product-description')
            
            # Extract product images
            image_urls = page.evaluate("""() => {
                return Array.from(document.querySelectorAll('.product-image img'))
                    .map(img => img.src);
            }""")
            
            # Extract specifications from a table
            specs = page.evaluate("""() => {
                const specs = {};
                document.querySelectorAll('.product-specs tr').forEach(row => {
                    const key = row.querySelector('th').innerText.trim();
                    const value = row.querySelector('td').innerText.trim();
                    specs[key] = value;
                });
                return specs;
            }""")
            
            # Check if the product is in stock
            in_stock = page.is_visible('.in-stock')
            
            return {
                'url': url,
                'title': title,
                'is_product': True,
                'product_name': product_name,
                'product_price': product_price,
                'description': product_description,
                'image_urls': image_urls,
                'specifications': specs,
                'in_stock': in_stock
            }
            
        except Exception as e:
            # Log the error and return partial data
            self.logger.error(f"Error extracting product data: {str(e)}")
            return {
                'url': url,
                'title': title,
                'is_product': True,
                'extraction_error': str(e)
            }
    
    def extract_links(self, page: Page, base_url: str) -> List[str]:
        """
        Override the extract_links method to focus on product category and product pages.
        
        Args:
            page: Playwright page object
            base_url: Base URL for resolving relative links
            
        Returns:
            List of extracted URLs to crawl next
        """
        # Get all links using the parent class method
        all_links = super().extract_links(page, base_url)
        
        # Prioritize product and category pages
        # (customize these patterns for your target site)
        priority_links = [
            link for link in all_links 
            if '/product/' in link or '/category/' in link or '/collection/' in link
        ]
        
        # Return priority links first, followed by other links
        return priority_links + [link for link in all_links if link not in priority_links]


def main():
    # Create a product crawler instance
    crawler = ProductCrawler(
        headless=True,
        max_depth=3,
        max_pages=50,
        request_interval=1.5,
        output_dir='product_data'
    )
    
    # Start crawling from a product category page
    start_url = "https://example-ecommerce-site.com/category/electronics"
    print(f"Starting product crawl at {start_url}")
    
    # Run the crawler
    data = crawler.crawl(start_url)
    
    # Print summary statistics
    total_products = sum(1 for item in data if item.get('is_product', False))
    print(f"Crawl completed. Visited {len(crawler.visited_urls)} pages.")
    print(f"Found {total_products} product pages.")
    print(f"Data saved to {crawler.output_dir} directory.")


if __name__ == "__main__":
    main() 