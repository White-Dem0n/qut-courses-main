from playwright.sync_api import sync_playwright
from datetime import datetime
import json
from pathlib import Path
import logging
import time
import asyncio

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "src" / "occupations" / "data"
RAW_DIR = DATA_DIR / "raw"

# Create data directories if they don't exist
RAW_DIR.mkdir(parents=True, exist_ok=True)

# Set up logging
logging.basicConfig(
    filename=RAW_DIR / "scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def scrape_immi_website(page, url):
    """Scrape occupations from the Department of Home Affairs website."""
    occupations = []
    try:
        logging.info(f"Accessing {url}")
        page.goto(url)

        # Wait for the table to load
        page.wait_for_selector("table.table", timeout=30000)

        # Get all tables
        tables = page.query_selector_all("table.table")

        for table in tables:
            # Get all rows except header
            rows = table.query_selector_all("tr:not(:first-child)")

            for row in rows:
                try:
                    columns = row.query_selector_all("td")
                    if len(columns) >= 4:
                        code = columns[0].inner_text().strip()
                        title = columns[1].inner_text().strip()
                        if code and title:
                            occupation = {
                                "code": code,
                                "title": title,
                                "skill_level": columns[2].inner_text().strip(),
                                "assessing_authority": columns[3].inner_text().strip(),
                                "source": "Department of Home Affairs",
                                "date_scraped": datetime.now().strftime("%Y-%m-%d"),
                            }
                            occupations.append(occupation)
                            logging.info(f"Found occupation: {code} - {title}")
                except Exception as e:
                    logging.error(f"Error parsing row: {str(e)}")
                    continue

    except Exception as e:
        logging.error(f"Error scraping IMMI website: {str(e)}")

    return occupations


def scrape_abs_website(page, url):
    """Scrape occupations from the ABS website."""
    occupations = []
    try:
        logging.info(f"Accessing {url}")
        page.goto(url)

        # Wait for the table to load
        page.wait_for_selector("table", timeout=30000)

        # Get all tables
        tables = page.query_selector_all("table")

        for table in tables:
            # Get all rows except header
            rows = table.query_selector_all("tr:not(:first-child)")

            for row in rows:
                try:
                    columns = row.query_selector_all("td")
                    if len(columns) >= 2:
                        code_text = columns[0].inner_text().strip()
                        title_text = columns[1].inner_text().strip()
                        if code_text and title_text:
                            # Extract skill level from code (first digit)
                            skill_level = (
                                code_text[0]
                                if code_text and code_text[0].isdigit()
                                else ""
                            )
                            occupation = {
                                "code": code_text,
                                "title": title_text,
                                "skill_level": skill_level,
                                "source": "Australian Bureau of Statistics",
                                "date_scraped": datetime.now().strftime("%Y-%m-%d"),
                            }
                            occupations.append(occupation)
                            logging.info(
                                f"Found occupation: {code_text} - {title_text}"
                            )
                except Exception as e:
                    logging.error(f"Error parsing row: {str(e)}")
                    continue

    except Exception as e:
        logging.error(f"Error scraping ABS website: {str(e)}")

    return occupations


def save_occupations(occupations, source_name):
    """Save occupations to a JSON file."""
    if occupations:
        output_file = RAW_DIR / f"occupations_{source_name}.json"

        # If file exists, load and merge with existing data
        existing_occupations = []
        if output_file.exists():
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    existing_occupations = data.get("occupations", [])
            except Exception as e:
                logging.error(f"Error reading existing file: {str(e)}")

        # Merge existing and new occupations, removing duplicates based on code
        all_occupations = {
            o["code"]: o for o in existing_occupations + occupations
        }.values()

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "source": source_name,
                    "date_scraped": datetime.now().strftime("%Y-%m-%d"),
                    "occupations": list(all_occupations),
                },
                f,
                indent=4,
                ensure_ascii=False,
            )
        logging.info(f"Saved {len(all_occupations)} occupations to {output_file}")
    else:
        logging.warning(f"No occupations found for {source_name}")


def run_scraper():
    """Run the scraper for all sources."""
    with sync_playwright() as p:
        try:
            # Launch browser
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # List of URLs to try
            sources = [
                {
                    "name": "immi",
                    "url": "https://immi.homeaffairs.gov.au/visas/working-in-australia/skill-occupation-list",
                    "scraper": scrape_immi_website,
                },
                {
                    "name": "abs",
                    "url": "https://www.abs.gov.au/statistics/classifications/anzsco-australian-and-new-zealand-standard-classification-occupations/2022/concordance-tables/anzsco-2022-structure",
                    "scraper": scrape_abs_website,
                },
                {
                    "name": "abs_concordance",
                    "url": "https://www.abs.gov.au/statistics/classifications/anzsco-australian-and-new-zealand-standard-classification-occupations/2022/concordance-tables/concordance-tables",
                    "scraper": scrape_abs_website,
                },
            ]

            for source in sources:
                try:
                    logging.info(
                        f"Starting to scrape {source['name']} from {source['url']}"
                    )
                    occupations = source["scraper"](page, source["url"])
                    save_occupations(occupations, source["name"])
                except Exception as e:
                    logging.error(f"Error processing {source['name']}: {str(e)}")
                    continue

            # Close browser
            context.close()
            browser.close()

        except Exception as e:
            logging.error(f"Error running scraper: {str(e)}")


if __name__ == "__main__":
    run_scraper()
