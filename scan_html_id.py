#!/usr/bin/env python3

# This script crawls a website starting from a given URL and searches for specific HTML element IDs.
# It prints the URLs of pages that contain at least one of the specified IDs and saves the results to a file.
# Usage: ./scan_html_ids.py https://example.com id1 id2 id3 ...
# Requirements: requests, beautifulsoup4
# Install with: pip install requests beautifulsoup4

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, urlunparse
import sys

visited = set()
matching_urls = {}

def crawl(url, target_ids, base_domain):
    if url in visited:
        return

    parsed = urlparse(url)

    # Skip external domains
    if parsed.netloc and parsed.netloc != base_domain:
        return
    # Skip mailto:, tel:, javascript, etc.
    if parsed.scheme not in ("http", "https", ""):
        return
    # Skip anchor links
    if parsed.fragment:
        return
    # Skip PDFs
    if parsed.path.lower().endswith(".pdf"):
        return

    visited.add(url)

    try:
        response = requests.get(url, timeout=10)
        content_type = response.headers.get("Content-Type", "").lower()
        if response.status_code != 200 or "text/html" not in content_type:
            return

        soup = BeautifulSoup(response.text, "html.parser")

        for target_id in target_ids:
            clean_url = urlunparse(parsed._replace(query='', fragment=''))
            if soup.find(id=target_id):
                if clean_url not in matching_urls:
                    matching_urls[clean_url] = []
                if target_id not in matching_urls[clean_url]:
                    matching_urls[clean_url].append(target_id)

        for link in soup.find_all("a", href=True):
            next_url = urljoin(url, link["href"])
            crawl(next_url, target_ids, base_domain)

    except Exception as e:
        print(f"❌ Error crawling {url}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: ./scan_html_ids.py https://example.com id1 id2 id3 ...")
        sys.exit(1)

    start_url = sys.argv[1]
    target_ids = sys.argv[2:]
    domain = urlparse(start_url).netloc

    print(f"🔎 Searching for IDs: {', '.join(target_ids)}")
    crawl(start_url, target_ids, domain)

    print("\n✅ Done! Pages containing at least one target ID:")
    with open("form_urls.txt", "w") as f:
        for url, ids_found in matching_urls.items():
            line = f"{url}"
            print(line)
            f.write(line + "\n")

    print("\n📁 Results saved to form_urls.txt")

