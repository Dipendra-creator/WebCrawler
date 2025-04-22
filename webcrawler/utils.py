"""
Utility functions for the Playwright web crawler.
"""

import os
import random
import json
from typing import Dict, List, Optional, Any
from pathlib import Path


def load_user_agents(filepath: Optional[str] = None) -> List[str]:
    """
    Load a list of user agents from a file.
    
    Args:
        filepath: Path to a file containing user agents (one per line).
                 If None, uses a default list.
    
    Returns:
        List of user agent strings
    """
    if filepath and os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return [line.strip() for line in f if line.strip()]
    
    # Default set of common user agents
    return [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.62",
    ]


def get_random_user_agent(filepath: Optional[str] = None) -> str:
    """
    Get a random user agent from the list.
    
    Args:
        filepath: Path to a file containing user agents.
        
    Returns:
        A random user agent string
    """
    user_agents = load_user_agents(filepath)
    return random.choice(user_agents)


def load_proxies(filepath: str) -> List[Dict[str, str]]:
    """
    Load a list of proxies from a file.
    
    Args:
        filepath: Path to a JSON file containing proxy configurations.
        
    Returns:
        List of proxy configuration dictionaries
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Proxy file not found: {filepath}")
    
    with open(filepath, 'r') as f:
        proxies = json.load(f)
    
    # Validate the proxy format
    for proxy in proxies:
        if not isinstance(proxy, dict) or 'server' not in proxy:
            raise ValueError(f"Invalid proxy format. Each proxy must have at least a 'server' key. Got: {proxy}")
    
    return proxies


def get_random_proxy(filepath: str) -> Dict[str, str]:
    """
    Get a random proxy from the list.
    
    Args:
        filepath: Path to a JSON file containing proxy configurations.
        
    Returns:
        A random proxy configuration dictionary
    """
    proxies = load_proxies(filepath)
    return random.choice(proxies)


def prepare_request_headers() -> Dict[str, str]:
    """
    Prepare a set of common headers for HTTP requests.
    
    Returns:
        Dictionary of HTTP headers
    """
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": get_random_user_agent()
    }


def is_robots_allowed(url: str, user_agent: str = "*") -> bool:
    """
    Check if the URL is allowed to be crawled according to robots.txt.
    This is a placeholder - in a real implementation, you'd use a proper
    robots.txt parser like 'robotexclusionrulesparser' or 'reppy'.
    
    Args:
        url: URL to check
        user_agent: User agent to check for
        
    Returns:
        True if allowed, False if not
    """
    # Placeholder for robots.txt checking
    # In a real implementation, you would:
    # 1. Get the robots.txt URL for the domain
    # 2. Download and parse the robots.txt
    # 3. Check if the URL is allowed for the given user agent
    # 
    # For now, we'll just return True as a placeholder
    return True


def save_cookies(cookies: List[Dict[str, Any]], filepath: str) -> None:
    """
    Save cookies to a file.
    
    Args:
        cookies: List of cookie dictionaries
        filepath: Path to save the cookies
    """
    with open(filepath, 'w') as f:
        json.dump(cookies, f, indent=2)


def load_cookies(filepath: str) -> List[Dict[str, Any]]:
    """
    Load cookies from a file.
    
    Args:
        filepath: Path to the cookies file
        
    Returns:
        List of cookie dictionaries
    """
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r') as f:
        return json.load(f) 