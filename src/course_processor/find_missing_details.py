import json
from pymongo import MongoClient
import os


def find_courses_with_missing_details():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["qut_courses"]

    # Get collections
    not_courses_collection = db["not_courses"]
    details_collection = db["course_details"]

    # Get all course codes from details collection
    courses_with_details = list(
        details_collection.find({}, {"course_code": 1, "course_name": 1})
    )
    courses_with_details_codes = {
        course["course_code"] for course in courses_with_details
    }
    print(f"Found {len(courses_with_details_codes)} courses with details")
    print("Sample course codes with details:", list(courses_with_details_codes)[:5])

    # Get all courses from not_courses collection
    not_courses = list(not_courses_collection.find({}))
    print(f"\nFound {len(not_courses)} courses that couldn't be processed")

    # Save unprocessed courses to JSON
    unprocessed_courses = []
    for course in not_courses:
        unprocessed_courses.append(
            {
                "url": course.get("url", ""),
                "error": course.get("error", ""),
                "import_date": course.get("import_date", ""),
            }
        )

    # Save to JSON file
    with open("unprocessed_courses.json", "w", encoding="utf-8") as f:
        json.dump(unprocessed_courses, f, indent=2, ensure_ascii=False)

    print(f"\nAnalysis results:")
    print(f"Courses with full details: {len(courses_with_details_codes)}")
    print(f"Courses that couldn't be processed: {len(not_courses)}")
    print(
        f"Total courses attempted: {len(courses_with_details_codes) + len(not_courses)}"
    )

    print("\nSample of courses that couldn't be processed:")
    for course in not_courses[:5]:
        print(
            f"- {course.get('url', 'No URL')} ({course.get('error', 'No error message')})"
        )

    print("\nFull list has been saved to 'unprocessed_courses.json'")

    # Close MongoDB connection
    client.close()


if __name__ == "__main__":
    find_courses_with_missing_details()
