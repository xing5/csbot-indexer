import logging
from bs4 import BeautifulSoup
import trafilatura
from trafilatura.settings import use_config
from urllib.parse import urlparse, urljoin, urldefrag
from content_indexer import index

# configuration for trafilatura
tftConfig = use_config()
tftConfig.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")
default_header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*"
    ";q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.google.com/",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def _crawl(url, base_url, visited=set(), root=False):
    if url in visited:
        return

    visited.add(url)
    logging.info(f"Processing {url}")

    page_content = trafilatura.fetch_url(url)

    # Process the content with Trafilatura
    extracted_data = trafilatura.bare_extraction(page_content, output_format='json', config=tftConfig)

    if extracted_data and extracted_data['url'] and extracted_data['raw_text']:
        url = extracted_data['url']
        if root:
            logging.info(f"hash this url: {url}")
        index(url, extracted_data['raw_text'])
        
    else:
        print("No data extracted.\n")
        return

    try:
        soup = BeautifulSoup(page_content, 'html.parser')

        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                next_url = urldefrag(urljoin(url, href)).url
                if next_url.startswith(base_url):
                    _crawl(next_url, url, visited)
    except Exception as e:
        logging.error(f"Error processing {url}: {e}")


def crawl_site(site_url: str, force_update: bool = False):
    """Crawl a site"""
    # verify the site_url is correct format 
    _crawl(site_url, site_url, set(), True)
    

