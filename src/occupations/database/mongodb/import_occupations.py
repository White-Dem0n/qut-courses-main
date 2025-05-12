import json
from pymongo import MongoClient
from datetime import datetime
from pathlib import Path


def import_occupations_to_mongodb():
    # Get the project root directory
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
    DATA_DIR = PROJECT_ROOT / "src" / "occupations" / "data"
    RAW_DIR = DATA_DIR / "raw"

    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client["qut_courses"]  # Using the same database as courses
    occupations_collection = db["occupations"]

    # Clear existing data
    occupations_collection.delete_many({})

    try:
        # Read the occupations JSON file
        occupations_file = RAW_DIR / "occupations.json"
        with open(occupations_file, "r", encoding="utf-8") as file:
            data = json.load(file)

            # Add import date
            data["import_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Insert the metadata
            metadata = {
                "source": data["source"],
                "date_scraped": data["date_scraped"],
                "import_date": data["import_date"],
            }
            occupations_collection.insert_one(metadata)

            # Insert all occupations
            if data["occupations"]:
                occupations_collection.insert_many(data["occupations"])

            print(f"Imported {len(data['occupations'])} occupations to MongoDB")

    except Exception as e:
        print(f"Error importing occupations: {e}")

    # Create indexes for better query performance
    occupations_collection.create_index("code")
    occupations_collection.create_index("title")

    print("MongoDB import completed successfully!")
    print("Collection: occupations")


if __name__ == "__main__":
    import_occupations_to_mongodb()
