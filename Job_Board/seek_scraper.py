import os
import json
import logging
import time
import random
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlencode

import cloudscraper
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from dotenv import load_dotenv
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/seek_scraper.log"), logging.StreamHandler()],
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


class SeekScraper:
    def __init__(self):
        self.setup_directories()
        self.proxy_manager = ProxyManager()
        self.ua = UserAgent()
        self.scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
        self.base_url = "https://www.seek.com.au"
        self.mongodb_available = False
        self.setup_mongodb()

    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data", exist_ok=True)

    def setup_mongodb(self):
        """Set up MongoDB connection if available."""
        try:
            import pymongo

            self.client = pymongo.MongoClient(
                os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
            )
            self.db = self.client[os.getenv("MONGODB_DB", "job_board")]
            self.collection = self.db["seek_jobs"]
            self.mongodb_available = True
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.warning(f"MongoDB not available: {e}. Will save to JSON files only.")

    def get_headers(self) -> Dict[str, str]:
        """Generate random headers for the request."""
        return {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Referer": self.base_url,
            "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
        }

    def make_request(self, url: str, retries: int = 3) -> Optional[requests.Response]:
        """Make a request with proxy support and retry logic."""
        for attempt in range(retries):
            try:
                proxy = self.proxy_manager.get_proxy()
                response = self.scraper.get(
                    url,
                    headers=self.get_headers(),
                    proxies=proxy,
                    timeout=int(os.getenv("REQUEST_TIMEOUT", 30)),
                )
                response.raise_for_status()
                return response
            except Exception as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
                if attempt == retries - 1:
                    logger.error(f"Failed to fetch {url} after {retries} attempts")
                    return None
                time.sleep(random.uniform(2, 5))

    def parse_job_listing(self, html: str) -> List[Dict]:
        """Parse job listings from Seek's HTML content."""
        soup = BeautifulSoup(html, "html.parser")
        jobs = []

        # Seek's job cards are in article elements with data-automation="normalJob"
        job_cards = soup.find_all("article", attrs={"data-automation": "normalJob"})

        for card in job_cards:
            try:
                # Extract job details
                title_elem = card.find("h3", attrs={"data-automation": "jobTitle"})
                company_elem = card.find("a", attrs={"data-automation": "jobCompany"})
                location_elem = card.find("a", attrs={"data-automation": "jobLocation"})
                salary_elem = card.find("span", attrs={"data-automation": "jobSalary"})
                job_type_elem = card.find("span", attrs={"data-automation": "jobType"})
                posted_date_elem = card.find(
                    "span", attrs={"data-automation": "jobListingDate"}
                )

                # Get job URL
                job_link = card.find("a", attrs={"data-automation": "jobTitle"})
                job_url = urljoin(self.base_url, job_link["href"]) if job_link else None

                job = {
                    "title": title_elem.text.strip() if title_elem else None,
                    "company": company_elem.text.strip() if company_elem else None,
                    "location": location_elem.text.strip() if location_elem else None,
                    "salary": salary_elem.text.strip() if salary_elem else None,
                    "job_type": job_type_elem.text.strip() if job_type_elem else None,
                    "posted_date": (
                        posted_date_elem.text.strip() if posted_date_elem else None
                    ),
                    "url": job_url,
                    "scraped_at": datetime.utcnow().isoformat(),
                }

                # Only add jobs with at least a title and company
                if job["title"] and job["company"]:
                    jobs.append(job)

            except Exception as e:
                logger.error(f"Error parsing job card: {e}")
                continue

        return jobs

    def save_to_mongodb(self, jobs: List[Dict]):
        """Save jobs to MongoDB if available."""
        if not jobs or not self.mongodb_available:
            return

        try:
            # Use update_one with upsert to avoid duplicates
            for job in jobs:
                self.collection.update_one(
                    {"url": job["url"]}, {"$set": job}, upsert=True
                )
            logger.info(f"Saved/Updated {len(jobs)} jobs to MongoDB")
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

    def build_search_url(
        self, keywords: str = "", location: str = "Australia", page: int = 1
    ) -> str:
        """Build Seek search URL with parameters."""
        params = {"keywords": keywords, "location": location, "page": page}
        return f"{self.base_url}/jobs?{urlencode(params)}"

    def scrape(
        self, keywords: str = "", location: str = "Australia", max_pages: int = 10
    ):
        """Main scraping method."""
        logger.info(
            f"Starting to scrape Seek jobs for keywords: {keywords}, location: {location}"
        )

        all_jobs = []
        for page in tqdm(range(1, max_pages + 1), desc="Scraping pages"):
            url = self.build_search_url(keywords, location, page)
            logger.info(f"Scraping page {page}: {url}")

            response = self.make_request(url)
            if not response:
                logger.warning(f"Failed to fetch page {page}, stopping pagination")
                break

            jobs = self.parse_job_listing(response.text)
            if not jobs:
                logger.info(f"No more jobs found on page {page}, stopping pagination")
                break

            all_jobs.extend(jobs)
            logger.info(f"Found {len(jobs)} jobs on page {page}")

            # Random delay between pages
            time.sleep(random.uniform(2, 5))

        if all_jobs:
            self.save_to_mongodb(all_jobs)
            self.save_to_json(
                all_jobs, f'seek_jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            )

        logger.info(f"Completed scraping Seek. Total jobs found: {len(all_jobs)}")


def main():
    load_dotenv()
    scraper = SeekScraper()

    # Example search parameters
    keywords = "python developer"  # Customize as needed
    location = "Australia"  # Customize as needed
    max_pages = 10  # Adjust as needed

    scraper.scrape(keywords=keywords, location=location, max_pages=max_pages)


if __name__ == "__main__":
    main()
