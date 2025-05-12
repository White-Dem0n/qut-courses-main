import subprocess
import os
import asyncio
import json
import sys
import logging
from datetime import datetime
from pathlib import Path

# Setup logging
log_dir = Path(__file__).parent.parent / "logs"
log_dir.mkdir(exist_ok=True)
logging.basicConfig(
    filename=log_dir / f'scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
# Also log to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCRIPTS_DIR = Path(__file__).parent / "course_processor" / "scripts"

# Create data directories if they don't exist
(DATA_DIR / "raw").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "processed").mkdir(parents=True, exist_ok=True)


class RateLimiter:
    def __init__(self, calls_per_second):
        self.calls_per_second = calls_per_second
        self.last_call = 0
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = asyncio.get_event_loop().time()
            time_passed = now - self.last_call
            if time_passed < 1.0 / self.calls_per_second:
                await asyncio.sleep(1.0 / self.calls_per_second - time_passed)
            self.last_call = asyncio.get_event_loop().time()


async def retry_with_backoff(func, max_retries=3, initial_delay=1):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = initial_delay * (2**attempt)
            logging.warning(
                f"Attempt {attempt + 1} failed, retrying in {delay} seconds..."
            )
            await asyncio.sleep(delay)


# Initialize rate limiter
rate_limiter = RateLimiter(calls_per_second=1)


# Async function for running scripts
async def run_script(script_name):
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        logging.error(f"Script not found: {script_path}")
        return

    async def _run():
        await rate_limiter.acquire()
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(script_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return process.returncode, stdout, stderr

    try:
        returncode, stdout, stderr = await retry_with_backoff(_run)
        if returncode == 0:
            logging.info(f"Script {script_name} completed successfully.")
            logging.debug(stdout.decode())
        else:
            logging.error(f"Script {script_name} failed with error code {returncode}.")
            logging.error(stderr.decode())
    except Exception as e:
        logging.error(f"Failed to run script {script_name} after retries: {e}")


# Function to run a script with arguments
async def run_script_with_args(script_name, *args):
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        logging.error(f"Script not found: {script_path}")
        return

    async def _run():
        await rate_limiter.acquire()
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(script_path),
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return process.returncode, stdout, stderr

    try:
        returncode, stdout, stderr = await retry_with_backoff(_run)
        if returncode == 0:
            logging.info(
                f"Script {script_name} completed successfully with args: {args}"
            )
            logging.debug(stdout.decode(errors="replace"))
        else:
            logging.error(
                f"Script {script_name} failed with error code {returncode} and args: {args}"
            )
            logging.error(stderr.decode(errors="replace"))
    except Exception as e:
        logging.error(
            f"Failed to run script {script_name} with args {args} after retries: {e}"
        )


# Check if courses.json exists. If it doesn't then get it
async def check_and_run():
    courses_file = DATA_DIR / "raw" / "courses.json"
    if courses_file.exists():
        logging.info("courses.json already exists")
    else:
        logging.info("courses.json does not exist. Fetching the list...")
        await run_script("PCI.py")


# Function to pull course information from the JSON file and plug into extract course information script
async def pull_course_information():
    courses_file = DATA_DIR / "raw" / "courses.json"
    try:
        with open(courses_file, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logging.error(f"Error reading courses file: {e}")
        return

    if not isinstance(data, dict) or "list_of_courses" not in data:
        logging.error("Invalid courses data structure")
        return

    total_courses = len(data["list_of_courses"])
    logging.info(f"Processing {total_courses} courses...")

    successful_courses = 0
    failed_courses = 0

    for i, course in enumerate(data["list_of_courses"]):
        try:
            course_code = course.get("courseCode")
            course_title = course.get("course_title")

            if not course_code or not course_title:
                logging.warning(f"Skipping invalid course data at index {i}")
                failed_courses += 1
                continue

            logging.info(
                f"Processing course {i+1}/{total_courses}: {course_code} - {course_title}"
            )
            await run_script_with_args("ECI.py", course_code, course_title)
            successful_courses += 1

        except Exception as e:
            logging.error(f"Error processing course {i}: {e}")
            failed_courses += 1
            continue

    logging.info(
        f"Course processing completed. Successful: {successful_courses}, Failed: {failed_courses}"
    )


# Main script
async def main():
    try:
        logging.info("Starting course scraping process")
        # Check if there is a course json file with all the course information.
        await check_and_run()

        # Run the script to pull course information
        await pull_course_information()
        logging.info("Course scraping process completed successfully")
    except Exception as e:
        logging.error(f"Fatal error in main process: {e}")
        sys.exit(1)


# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
