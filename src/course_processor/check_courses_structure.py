from pymongo import MongoClient
import json


def check_courses_structure():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["qut_courses"]

    # Get collections
    courses_collection = db["courses"]

    # Get a sample of courses
    print("Sample of courses in the database:")
    for course in courses_collection.find().limit(5):
        print("\nCourse document:")
        print(json.dumps(course, indent=2, default=str))

    # Count courses with different source types
    total = courses_collection.count_documents({})
    with_url = courses_collection.count_documents(
        {"source": {"$regex": "qut.edu.au/courses/"}}
    )
    with_list = courses_collection.count_documents(
        {"source": {"$regex": "active-courses-list"}}
    )
    empty = courses_collection.count_documents({"source": ""})

    print(f"\nAnalysis:")
    print(f"Total courses: {total}")
    print(f"Courses with course URLs: {with_url}")
    print(f"Courses with list URL: {with_list}")
    print(f"Courses with empty source: {empty}")

    client.close()


if __name__ == "__main__":
    check_courses_structure()
