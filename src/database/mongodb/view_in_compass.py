import pymongo
from pymongo import MongoClient
import json
from pprint import pprint


def check_mongodb_connection():
    try:
        # Try to connect to MongoDB
        client = MongoClient(
            "mongodb://localhost:27017/", serverSelectionTimeoutMS=5000
        )
        client.server_info()  # This will raise an exception if connection fails
        print("Successfully connected to MongoDB!")
        return True
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("\nPlease make sure MongoDB is running and accessible.")
        return False


def show_compass_instructions():
    print("\n" + "=" * 80)
    print("VIEWING DATA IN MONGODB COMPASS")
    print("=" * 80)
    print("\nFollow these steps to view your data in MongoDB Compass:")
    print("\n1. Open MongoDB Compass")
    print("2. Connect to: mongodb://localhost:27017")
    print("3. Click on the 'qut_courses' database")
    print(
        "4. You'll see three collections: 'courses', 'course_details', and 'not_courses'"
    )
    print("5. Click on any collection to view its documents")
    print("\nExample queries you can run in Compass:")
    print("\nFor courses collection:")
    print("  - Find all courses: {}")
    print('  - Find a specific course: {courseCode: "AB05"}')
    print("\nFor course_details collection:")
    print('  - Find courses with ATAR rank above 80: {atar_rank: {$gt: "80.00"}}')
    print('  - Find courses by delivery location: {delivery_location: "Gardens Point"}')
    print('  - Find courses by duration: {"durations.duration": "3 years full-time"}')
    print("\nFor not_courses collection:")
    print("  - Find all not processed courses: {}")
    print('  - Find courses with specific errors: {error: "Course code is missing"}')
    print("\n" + "=" * 80)


def show_database_summary():
    try:
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

        print("\n" + "=" * 80)
        print("DATABASE SUMMARY")
        print("=" * 80)
        print(f"Database: qut_courses")
        print(f"Total courses: {courses_count}")
        print(f"Total course details: {course_details_count}")
        print(f"Total not processed courses: {not_courses_count}")
        print("=" * 80)

        # Show sample queries
        print("\nSAMPLE QUERIES YOU CAN RUN IN COMPASS:")
        print("\n1. Find all courses with ATAR rank above 80:")
        print("   Collection: course_details")
        print('   Query: {atar_rank: {$gt: "80.00"}}')

        print("\n2. Find all courses delivered at Gardens Point:")
        print("   Collection: course_details")
        print('   Query: {delivery_location: "Gardens Point"}')

        print("\n3. Find all courses with 3 years full-time duration:")
        print("   Collection: course_details")
        print('   Query: {"durations.duration": "3 years full-time"}')

        print("\n4. Find all courses with 'Business' in the title:")
        print("   Collection: courses")
        print('   Query: {course_title: {$regex: "Business", $options: "i"}}')

        print("\n5. Find all possible careers for a specific course:")
        print("   Collection: course_details")
        print('   Query: {course_code: "AB05"}')
        print(
            "   Then look at the 'what_to_expect-careers_and_outcome.Possible Careers' field"
        )

        print("=" * 80)

    except Exception as e:
        print(f"Error getting database summary: {e}")


if __name__ == "__main__":
    if check_mongodb_connection():
        show_database_summary()
        show_compass_instructions()
    else:
        print("\nPlease make sure MongoDB is running and try again.")
