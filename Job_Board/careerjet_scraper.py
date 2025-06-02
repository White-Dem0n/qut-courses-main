import os
import json
import time
import random
import logging
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlencode

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/careerjet_scraper.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class CareerJetScraper:
    def __init__(self):
        self.setup_directories()
        self.base_url = "https://www.careerjet.com.au/jobs?l=Australia&nw=1&s="
        self.max_retries = 3
        self.retry_delay = 5

    def setup_directories(self):
        """Create necessary directories if they don't exist."""
        os.makedirs("logs", exist_ok=True)
        os.makedirs("data", exist_ok=True)

    def parse_job_listing(self, html_content: str) -> List[Dict]:
        """Parse job listings from CareerJet's page using BeautifulSoup."""
        jobs = []
        soup = BeautifulSoup(html_content, "html.parser")
        # The job cards are likely under ul > li > article
        job_cards = soup.select("ul li article")

        for card in job_cards:  # No limit on the number of jobs
            try:
                # Title is in the first <p> inside <article>
                title_elem = card.find("p")
                title = title_elem.text.strip() if title_elem else None

                # Location is in the second <ul> inside <article>
                location_elem = card.find("ul", class_="location")
                location = (
                    location_elem.find("li").text.strip() if location_elem else None
                )

                # Salary is in the third <ul> inside <article>
                salary_elem = card.find("ul", class_="salary")
                salary = salary_elem.find("li").text.strip() if salary_elem else None

                # Description is in the <div> inside <article>
                description_elem = card.find("div")
                description = (
                    description_elem.text.strip() if description_elem else None
                )

                # Posted date is in the <footer> inside <article>
                date_elem = card.find("footer").find("ul").find("li").find("span")
                posted_date = date_elem.text.strip() if date_elem else None

                # Link to job details
                link_elem = card.find("a", href=True)
                job_url = link_elem["href"] if link_elem else None

                job = {
                    "title": title,
                    "location": location,
                    "url": job_url,
                    "description": description,
                    "salary": salary,
                    "posted_date": posted_date,
                    "source": "CareerJet",
                    "scraped_at": datetime.utcnow().isoformat(),
                }
                jobs.append(job)
                logger.info(f"Successfully scraped job: {job['title']}")

            except Exception as e:
                logger.error(f"Error parsing job card: {e}")
                continue

        return jobs

    def save_to_json(self, jobs: List[Dict], filename: str):
        """Save jobs to a JSON file in the Job_Board directory."""
        if not jobs:
            return

        try:
            filepath = os.path.join("Job_Board", filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(jobs, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(jobs)} jobs to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save jobs to JSON: {e}")

    def scrape(self, max_pages: int = 70):
        """Main scraping method."""
        logger.info("Starting to scrape CareerJet jobs")
        all_jobs = []

        try:
            for page in tqdm(range(1, max_pages + 1), desc="Scraping pages"):
                url = f"{self.base_url}&p={page}"
                logger.info(f"Scraping page {page}: {url}")

                # Retry mechanism for page loading
                for attempt in range(self.max_retries):
                    try:
                        headers = {
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                        }
                        response = requests.get(url, headers=headers)
                        response.raise_for_status()
                        jobs = self.parse_job_listing(response.text)
                        break
                    except requests.RequestException as e:
                        if attempt == self.max_retries - 1:
                            logger.error(
                                f"Failed to load page {page} after {self.max_retries} attempts: {e}"
                            )
                            raise
                        logger.warning(
                            f"Failed to load page {page}, retrying... ({attempt + 1}/{self.max_retries})"
                        )
                        time.sleep(self.retry_delay)

                if not jobs:
                    logger.info(
                        f"No more jobs found on page {page}, stopping pagination"
                    )
                    break

                all_jobs.extend(jobs)
                logger.info(f"Found {len(jobs)} jobs on page {page}")

                # Fixed delay between pages
                time.sleep(2)

        except Exception as e:
            logger.error(f"Error during scraping: {e}")

        if all_jobs:
            self.save_to_json(
                all_jobs,
                f'careerjet_jobs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            )

        logger.info(f"Completed scraping CareerJet. Total jobs found: {len(all_jobs)}")


def main():
    load_dotenv()
    scraper = CareerJetScraper()
    scraper.scrape(max_pages=70)


if __name__ == "__main__":
    main()
