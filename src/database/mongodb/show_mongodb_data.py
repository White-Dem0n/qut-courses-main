import pymongo
from pymongo import MongoClient
import json
from pprint import pprint


def show_mongodb_data():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")

    # Get the database
    db = client["qut_courses"]

    # Get collections
    courses_collection = db["courses"]
    course_details_collection = db["course_details"]
    not_courses_collection = db["not_courses"]

    # Count documents in each collection
    courses_count = courses_collection.count_documents({})
    course_details_count = course_details_collection.count_documents({})
    not_courses_count = not_courses_collection.count_documents({})

    print(f"\n{'='*50}")
    print(f"MongoDB Database: qut_courses")
    print(f"{'='*50}")
    print(f"Total courses: {courses_count}")
    print(f"Total course details: {course_details_count}")
    print(f"Total not processed courses: {not_courses_count}")
    print(f"{'='*50}\n")

    # Show sample data from courses collection
    print(f"{'='*50}")
    print(f"Sample data from courses collection:")
    print(f"{'='*50}")
    for i, course in enumerate(courses_collection.find().limit(5)):
        print(f"Course {i+1}:")
        pprint(course)
        print()

    # Show sample data from course_details collection
    print(f"{'='*50}")
    print(f"Sample data from course_details collection:")
    print(f"{'='*50}")
    for i, course_detail in enumerate(course_details_collection.find().limit(3)):
        print(f"Course Detail {i+1}:")
        pprint(course_detail)
        print()

    # Show sample data from not_courses collection
    print(f"{'='*50}")
    print(f"Sample data from not_courses collection:")
    print(f"{'='*50}")
    for i, not_course in enumerate(not_courses_collection.find().limit(3)):
        print(f"Not Processed Course {i+1}:")
        pprint(not_course)
        print()

    print(f"{'='*50}")
    print(
        f"To view more data, use MongoDB Compass or run queries in the MongoDB shell."
    )
    print(f"{'='*50}")


if __name__ == "__main__":
    show_mongodb_data()
