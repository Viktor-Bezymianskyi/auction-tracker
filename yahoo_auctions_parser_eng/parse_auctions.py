import os
import csv
import time
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
import sys
from dotenv import load_dotenv
from search_config.excluded_words import is_excluded
from search_config.quantity_extractor import extract_quantity
from search_config.status_extractor import extract_status
from settings.config import load_proxy_settings, DEBUG_MODE, DEBUG_DIR

# Load environment variables
load_dotenv()


@dataclass
class AuctionItem:
    """
    Class for storing Yahoo Auctions item information.
    Uses Python dataclass for automatic method generation.

    Attributes:
        id (str): Unique item ID
        title (str): Item title
        price (int): Current price in JPY
        seller_id (str): Seller ID
        seller_name (str): Seller name
        end_time (str): Auction end time
        bids (int): Number of bids
        url (str): Item URL
        image_url (str): Image URL
        shipping_info (str): Shipping information
        quantity (int): Item quantity
        status (str): Item condition status
    """
    id: str
    title: str
    price: int
    seller_id: str
    seller_name: str
    end_time: str
    bids: int
    url: str
    image_url: str
    shipping_info: str
    quantity: int = 1
    status: str = ''


class YahooAuctionsParser:
    """
    Main class for parsing Yahoo Auctions.

    Parameters:
        proxy (dict, optional): Proxy settings in format:
            {
                'http': 'http://user:pass@host:port',
                'https': 'https://user:pass@host:port'
            }
    """

    def __init__(self, proxy: Optional[dict] = None):
        self.proxy = proxy or {
            'http': os.getenv('PROXY_1'),
            'https': os.getenv('PROXY_2'),
            'socks5': os.getenv('PROXY_SOCKS5')
        }
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create and configure HTTP session with headers and proxy"""
        session = requests.Session()
        if self.proxy:
            session.proxies.update(self.proxy)

        session.headers.update({
            'User-Agent': os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        })
        return session

    # ... (other methods translated similarly) ...


def save_items_to_csv(items: List[AuctionItem], filename: str) -> None:
    """
    Save auction items to CSV file.

    Parameters:
        items (List[AuctionItem]): List of items to save
        filename (str): Output filename (without path)
    """
    if not items:
        print("No data to save")
        return

    os.makedirs('results', exist_ok=True)
    filepath = os.path.join('results', filename)

    fieldnames = list(AuctionItem.__annotations__.keys())

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in items:
            writer.writerow(item.__dict__)

    print(f"Saved {len(items)} items to {filepath}")
