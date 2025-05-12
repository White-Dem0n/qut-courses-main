import json
from pymongo import MongoClient
import os


def find_filtered_courses():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["qut_courses"]

    # Get all collections
    courses_collection = db["courses"]
    details_collection = db["course_details"]
    not_courses_collection = db["not_courses"]

    # Get counts
    total_courses = courses_collection.count_documents({})
    processed_courses = details_collection.count_documents({})
    unprocessed_courses = not_courses_collection.count_documents({})

    # Get all course codes from processed and unprocessed courses
    processed_codes = set()
    for course in details_collection.find({}, {"course_code": 1}):
        processed_codes.add(course["course_code"])

    for course in not_courses_collection.find({}, {"course_code": 1}):
        if "course_code" in course:
            processed_codes.add(course["course_code"])

    # Find filtered courses
    filtered_courses = []
    for course in courses_collection.find({}):
        course_code = course.get("courseCode")
        if course_code and course_code not in processed_codes:
            filtered_courses.append(
                {
                    "course_code": course_code,
                    "course_title": course.get("course_title", ""),
                    "day_obtained": course.get("day_obtained", ""),
                    "import_date": course.get("import_date", ""),
                }
            )

    # Save to JSON file
    with open("filtered_courses.json", "w", encoding="utf-8") as f:
        json.dump(filtered_courses, f, indent=2, ensure_ascii=False)

    print(f"\nAnalysis results:")
    print(f"Total courses in database: {total_courses}")
    print(f"Successfully processed courses: {processed_courses}")
    print(f"Unprocessed courses: {unprocessed_courses}")
    print(f"Filtered out courses: {len(filtered_courses)}")

    if filtered_courses:
        print("\nSample of filtered courses:")
        for course in filtered_courses[:5]:
            print(f"- {course['course_code']}: {course['course_title']}")

    print("\nFull list has been saved to 'filtered_courses.json'")

    # Close MongoDB connection
    client.close()


if __name__ == "__main__":
    find_filtered_courses()
