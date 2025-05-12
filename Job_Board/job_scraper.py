import os
import json
import logging
import time
import random
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from dotenv import load_dotenv
import pymongo
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/scraper.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.current_proxy = None
        self.last_rotation = 0
        self.rotation_interval = int(os.getenv("PROXY_ROTATION_INTERVAL", 300))
        self._load_proxies()

    def _load_proxies(self):
        """Load proxies from environment variables or proxy list file."""
        proxy_list = os.getenv("PROXY_LIST", "").split(",")
        if proxy_list and proxy_list[0]:
            self.proxies = [p.strip() for p in proxy_list if p.strip()]
        else:
            # Load from proxy list file if exists
            try:
                with open("proxy_list.txt", "r") as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                logger.warning("No proxy list found. Running without proxies.")

    def get_proxy(self) -> Optional[Dict[str, str]]:
        """Get a proxy for the request."""
        if not self.proxies:
            return None

        current_time = time.time()
        if (
            not self.current_proxy
            or current_time - self.last_rotation > self.rotation_interval
        ):
            self.current_proxy = random.choice(self.proxies)
            self.last_rotation = current_time

        return {"http": self.current_proxy, "https": self.current_proxy}


class JobScraper:
    def __init__(self):
        self.setup_directories()
        self.proxy_manager = ProxyManager()
        self.ua = UserAgent()
        self.session = requests.Session()
        self.setup_mongodb()

    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data", exist_ok=True)

    def setup_mongodb(self):
        """Set up MongoDB connection."""
        try:
            self.client = pymongo.MongoClient(
                os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
            )
            self.db = self.client[os.getenv("MONGODB_DB", "job_board")]
            self.collection = self.db[os.getenv("MONGODB_COLLECTION", "jobs")]
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    def get_headers(self) -> Dict[str, str]:
        """Generate random headers for the request."""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    def make_request(self, url: str, retries: int = 3) -> Optional[requests.Response]:
        """Make a request with proxy support and retry logic."""
        for attempt in range(retries):
            try:
                proxy = self.proxy_manager.get_proxy()
                response = self.session.get(
                    url,
                    headers=self.get_headers(),
                    proxies=proxy,
                    timeout=int(os.getenv("REQUEST_TIMEOUT", 30)),
                )
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
                time.sleep(random.uniform(1, 3))

    def parse_job_listing(self, html: str) -> List[Dict]:
        """Parse job listings from HTML content."""
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        # This is a placeholder - implement specific parsing logic for your target site
        job_cards = soup.find_all("div", class_="job-card")  # Adjust selector

        for card in job_cards:
            try:
                job = {
                    "title": card.find("h2").text.strip(),
                    "company": card.find("div", class_="company").text.strip(),
                    "location": card.find("div", class_="location").text.strip(),
                    "url": urljoin(self.base_url, card.find("a")["href"]),
                    "posted_date": card.find("div", class_="date").text.strip(),
                    "scraped_at": datetime.utcnow().isoformat(),
                }
                jobs.append(job)
            except Exception as e:
                logger.error(f"Error parsing job card: {e}")
                continue

        return jobs

    def save_to_mongodb(self, jobs: List[Dict]):
        """Save jobs to MongoDB."""
        if not jobs:
            return

        try:
            result = self.collection.insert_many(jobs)
            logger.info(f"Saved {len(result.inserted_ids)} jobs to MongoDB")
        except Exception as e:
            logger.error(f"Failed to save jobs to MongoDB: {e}")

    def save_to_json(self, jobs: List[Dict], filename: str):
        """Save jobs to a JSON file."""
        if not jobs:
            return

        try:
            with open(f"data/{filename}", "w", encoding="utf-8") as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(jobs)} jobs to {filename}")
        except Exception as e:
            logger.error(f"Failed to save jobs to JSON: {e}")

    def scrape(self, url: str):
        """Main scraping method."""
        logger.info(f"Starting to scrape {url}")

        response = self.make_request(url)
        if not response:
            return

        jobs = self.parse_job_listing(response.text)
        if jobs:
            self.save_to_mongodb(jobs)
            self.save_to_json(
                jobs, f'jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )

        logger.info(f"Completed scraping {url}")


def main():
    load_dotenv()
    scraper = JobScraper()

    # Add your target URLs here
    urls = [
        "https://example.com/jobs",
        # Add more URLs as needed
    ]

    for url in urls:
        scraper.scrape(url)
        time.sleep(random.uniform(1, 3))  # Random delay between requests


if __name__ == "__main__":
    main()
