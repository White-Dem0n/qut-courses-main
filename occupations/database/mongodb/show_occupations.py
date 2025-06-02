from pymongo import MongoClient
from datetime import datetime


def show_occupation_data():
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["qut_courses"]
    occupations_collection = db["occupations"]

    # Get total count of occupations
    total_occupations = occupations_collection.count_documents({})
    metadata = occupations_collection.find_one({"source": {"$exists": True}})

    print("=" * 50)
    print("MongoDB Database: qut_courses")
    print("Collection: occupations")
    print("=" * 50)
    print(f"Total occupations: {total_occupations}")
    if metadata:
        print(f"Source: {metadata.get('source', 'N/A')}")
        print(f"Date scraped: {metadata.get('date_scraped', 'N/A')}")
        print(f"Last import: {metadata.get('import_date', 'N/A')}")
    print("=" * 50)

    # Show sample data
    print("\nSample occupations:")
    print("=" * 50)
    sample_occupations = occupations_collection.find(
        {"code": {"$exists": True}},
        {"_id": 0, "code": 1, "title": 1, "skill_level": 1, "assessing_authority": 1},
    ).limit(5)

    for i, occupation in enumerate(sample_occupations, 1):
        print(f"\nOccupation {i}:")
        print(f"Code: {occupation.get('code', 'N/A')}")
        print(f"Title: {occupation.get('title', 'N/A')}")
        print(f"Skill Level: {occupation.get('skill_level', 'N/A')}")
        print(f"Assessing Authority: {occupation.get('assessing_authority', 'N/A')}")

    print("\n" + "=" * 50)
    print("To view more data, use MongoDB Compass or run queries in the MongoDB shell.")
    print("=" * 50)


if __name__ == "__main__":
    show_occupation_data()
