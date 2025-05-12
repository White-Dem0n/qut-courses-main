from pymongo import MongoClient


def check_collections_structure():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["qut_courses"]

    # Check courses collection
    courses_collection = db["courses"]
    course_sample = courses_collection.find_one()
    if course_sample:
        print("Sample course document structure:")
        print(course_sample.keys())

    # Check course_details collection
    details_collection = db["course_details"]
    detail_sample = details_collection.find_one()
    if detail_sample:
        print("\nSample course_details document structure:")
        print(detail_sample.keys())

    # Print counts
    print(f"\nNumber of courses: {courses_collection.count_documents({})}")
    print(f"Number of course details: {details_collection.count_documents({})}")

    client.close()


if __name__ == "__main__":
    check_collections_structure()
