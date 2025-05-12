import os
import json
import pymongo
from pymongo import MongoClient
from datetime import datetime
from pathlib import Path


def import_to_mongodb():
    # Get the project root directory
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    RAW_DIR = DATA_DIR / "raw"

    # Connect to MongoDB
    # If MongoDB is running locally on the default port
    client = MongoClient("mongodb://localhost:27017/")

    # Create or get the database
    db = client["qut_courses"]

    # Create collections
    courses_collection = db["courses"]
    course_details_collection = db["course_details"]

    # Clear existing data (optional)
    courses_collection.delete_many({})
    course_details_collection.delete_many({})

    # Import the main courses list
    try:
        courses_file = RAW_DIR / "courses.json"
        with open(courses_file, "r", encoding="utf-8") as file:
            courses_data = json.load(file)

            # Insert the source and date information
            source_info = {
                "source": courses_data.get("source", ""),
                "day_obtained": courses_data.get("day_obtained", ""),
                "import_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            courses_collection.insert_one(source_info)

            # Insert each course
            for course in courses_data.get("list_of_courses", []):
                courses_collection.insert_one(course)

            print(
                f"Imported {len(courses_data.get('list_of_courses', []))} courses to MongoDB"
            )
    except Exception as e:
        print(f"Error importing courses.json: {e}")

    # Import individual course details
    course_files = [
        f
        for f in os.listdir(RAW_DIR)
        if f.endswith(".json") and f != "courses.json" and f != "not_courses.json"
    ]

    for file_name in course_files:
        try:
            file_path = RAW_DIR / file_name
            with open(file_path, "r", encoding="utf-8") as file:
                course_detail = json.load(file)

                # Add import date
                course_detail["import_date"] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                # Insert into course_details collection
                course_details_collection.insert_one(course_detail)

                print(f"Imported {file_name} to MongoDB")
        except Exception as e:
            print(f"Error importing {file_name}: {e}")

    # Import not_courses.json if it exists
    not_courses_file = RAW_DIR / "not_courses.json"
    if not_courses_file.exists():
        try:
            with open(not_courses_file, "r", encoding="utf-8") as file:
                not_courses = json.load(file)

                # Create a collection for courses that couldn't be processed
                not_courses_collection = db["not_courses"]
                not_courses_collection.delete_many({})

                # Add import date to each entry
                for entry in not_courses:
                    entry["import_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Insert all entries
                if not_courses:
                    not_courses_collection.insert_many(not_courses)

                print(f"Imported {len(not_courses)} not processed courses to MongoDB")
        except Exception as e:
            print(f"Error importing not_courses.json: {e}")

    # Create indexes for better query performance
    courses_collection.create_index("courseCode")
    course_details_collection.create_index("course_code")

    print("MongoDB import completed successfully!")
    print(f"Database: qut_courses")
    print(f"Collections: courses, course_details, not_courses")


if __name__ == "__main__":
    import_to_mongodb()
