# The purpose of this script is to pull information from the each course information.
import sys
import scrapy
from scrapy_splash import SplashRequest
from scrapy.crawler import CrawlerProcess
import subprocess
from datetime import datetime
import re
import json
import unicodedata
import pdfplumber
import requests
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"

# Create data directories if they don't exist
RAW_DIR.mkdir(parents=True, exist_ok=True)


class MySpider(scrapy.Spider):
    name = "course_spider"
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    }

    def __init__(self, courseLink=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.courseLink = courseLink

    def start_requests(self):
        if self.courseLink:
            yield SplashRequest(
                url=self.courseLink,
                callback=self.parse,
                args={"wait": 10},  # Adjust wait time if needed
            )
        else:
            self.logger.error("No course link provided.")

    @staticmethod
    def normalize_text(text):
        # Replace smart quotes and other typographic characters with ASCII equivalents
        text = text.replace(
            """,'"')  # right single quote
        text = text.replace(""",
            '"',
        )  # left single quote
        text = text.replace('"', '"')  # left double quote
        text = text.replace('"', '"')  # right double quote
        text = unicodedata.normalize("NFKC", text)  # normalize Unicode
        return text

    #    Handles courses with missing data by logging and saving to `not_courses.json`
    def handle_missing_course(self, url, error_message, missing_fields=None):
        missing_course = {
            "url": url,
            "error": error_message,
        }
        if missing_fields:
            missing_course["missing_fields"] = missing_fields

        not_courses_file = RAW_DIR / "not_courses.json"
        try:
            with open(not_courses_file, "r", encoding="utf-8") as f:
                not_courses = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            not_courses = []

        not_courses.append(missing_course)

        with open(not_courses_file, "w", encoding="utf-8") as f:
            json.dump(not_courses, f, indent=4)

        self.logger.warning(f"Missing or invalid course data for URL: {url}")

    def parse(self, response):
        response_file = RAW_DIR / "response.html"
        with open(response_file, "w", encoding="utf-8") as f:
            f.write(response.text)

        try:
            # Extract course name
            course_name = response.css(
                'span[data-course-map-key="courseTitle"]::text'
            ).get()
            course_name = course_name.strip() if course_name else None

            course_code = response.css(
                'dd[data-course-map-key="reqTabCourseCode"]::text'
            ).get()
            course_code = course_code.strip() if course_code else None

            if not course_name:
                raise ValueError("Course name is missing")

            if not course_code:
                raise ValueError("Course code is missing")

        except Exception as e:
            self.handle_missing_course(response.url, str(e))
            return  # Exit early

        # Extract course code from the ATAR/Selection rank section
        course_code = response.css(
            'dd[data-course-map-key="reqTabCourseCode"]::text'
        ).get()
        course_code = course_code.strip()

        # Extract durations (Domestic and International)
        durations = response.css("div.duration-icon li[data-course-audience]")
        duration_data = []
        for duration in durations:
            audience = duration.css("::attr(data-course-audience)").get()  # DOM or INT
            text = duration.css("::text").get().strip()  # Duration text
            duration_data.append({"audience": audience, "duration": text})

        # Extract main description
        main_description = response.css("#details-and-units-tab p::text").get()

        # Extract delivery location
        delivery_location = response.css(
            'div.col-sm-10 b:contains("Delivery") + ul li::text'
        ).get()

        # Extract ATAR/Selection Rank
        atar_rank = response.css("dd.rank.inverted::text").get()

        # Extract QTAC Code
        qtac_code = response.css(
            'b[data-course-audience="DOM"]:contains("QTAC code") + ul li::text'
        ).get()

        # Extract CRICOS Code
        cricos_code = response.css(
            'b[data-course-audience="INT"]:contains("CRICOS") + ul li::text'
        ).get()

        # Extract details and units
        details_and_units = response.css("#details-and-units-tab ol li::text").getall()
        seen = set()
        cleaned_details_and_units = []
        for detail in details_and_units:
            stripped_detail = detail.strip()
            if stripped_detail and stripped_detail not in seen:
                cleaned_details_and_units.append(stripped_detail)
                seen.add(stripped_detail)

        # Extract highlights
        highlights = response.css(
            'div.container.course-highlights[data-course-audience="DOM"] ul li::text'
        ).getall()
        cleaned_highlights = [
            MySpider.normalize_text(highlight.strip())
            for highlight in highlights
            if highlight and highlight.strip()
        ]

        # Extract all sections dynamically
        panel = response.css("div.panel-content.row")
        dynamic_sections = {}

        # Go through all .course-detail-item blocks inside this panel
        for section in panel.css("div.course-detail-item"):
            audience = section.attrib.get("data-course-audience", "")
            if "DOM" not in audience:
                continue  # Skip if it's not for DOM

            # Extract title
            title = section.css("h3::text").get()
            title = title.strip() if title else "Untitled Section"

            # Extract all text including inside <a> tags
            raw_texts = section.xpath(".//p//text()").getall()
            content = [
                MySpider.normalize_text(text.strip())
                for text in raw_texts
                if text.strip()
            ]

            dynamic_sections[title] = content

        # Extract possible careers
        possible_careers = response.css(
            'div.course-possible-careers[data-course-map-key="careerOutcomesList"] ul li::text'
        ).getall()
        possible_careers = [
            career.strip() for career in possible_careers if career.strip()
        ]

        if possible_careers:
            dynamic_sections["Possible Careers"] = possible_careers

        # Extract JSON-LD and get courseCode + identifier
        json_ld = response.xpath('//script[@type="application/ld+json"]/text()').get()
        identifier = json.loads(json_ld).get("identifier", None) if json_ld else None

        # Build the extracted data dictionary
        extracted_data = {
            "course_name": course_name,
            "course_code": course_code,
            "identifier": identifier,
            "durations": duration_data,
            "delivery_location": delivery_location,
            "atar_rank": atar_rank,
            "qtac_code": qtac_code,
            "cricos_code": cricos_code,
            "main_description": main_description,
            "details_and_units": cleaned_details_and_units,
            "highlights": cleaned_highlights,
            "what_to_expect-careers_and_outcome": dynamic_sections,
            "url": self.courseLink,
            "day_obtained": datetime.now().strftime("%Y-%m-%d"),
        }

        # Save the extracted data to a separate JSON file for each course
        if course_code:
            output_file = RAW_DIR / f"{course_code}.json"
        else:
            output_file = RAW_DIR / f"{course_name.replace(' ', '_').lower()}.json"

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(extracted_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing to {output_file}: {e}")

        # Yield the extracted data as output
        yield extracted_data


# Access arguments passed to the script
course_code = sys.argv[1]  # First argument
course_title = sys.argv[2]  # Second argument


course_title = re.sub(r"\s+", "-", course_title).lower()
course_title = re.sub(r"-{2,}", "-", course_title)  # Remove extra dashes
course_title = re.sub(r"[()]", "", course_title)  # Remove parentheses

courseLink = f"https://www.qut.edu.au/courses/{course_title}"
# courseLink = f"http://127.0.0.1:5500/scripts/responseForCourse.html"

# print(f"Processing course: {course_code} - {courseLink}")

# Run the spider with the course_link argument
process = CrawlerProcess()
process.crawl(MySpider, courseLink=courseLink)
process.start()
