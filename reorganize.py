import os
import shutil


def move_file(src, dst):
    try:
        shutil.move(src, dst)
        print(f"Moved {src} to {dst}")
    except Exception as e:
        print(f"Error moving {src}: {str(e)}")


# Move LinkedIn scraper files
move_file("linkedin_jobs", "src/scrapers/linkedin_jobs")

# Move occupation scraper files
move_file("skilled_occupations", "src/scrapers/occupations")
move_file("occupation_scraper.py", "src/scrapers/occupations/occupation_scraper.py")
move_file("occupations_spider.py", "src/scrapers/occupations/occupations_spider.py")

# Move course processor files
move_file("scripts", "src/course_processor/scripts")
move_file("course_details", "src/course_processor/course_details")
move_file("find_filtered_courses.py", "src/course_processor/find_filtered_courses.py")
move_file(
    "check_courses_structure.py", "src/course_processor/check_courses_structure.py"
)
move_file("find_missing_details.py", "src/course_processor/find_missing_details.py")

# Move database files
move_file("import_to_mongodb.py", "src/database/mongodb/import_to_mongodb.py")
move_file(
    "check_mongodb_structure.py", "src/database/mongodb/check_mongodb_structure.py"
)
move_file("view_in_compass.py", "src/database/mongodb/view_in_compass.py")
move_file("show_mongodb_data.py", "src/database/mongodb/show_mongodb_data.py")
move_file("MONGODB_SETUP.md", "docs/MONGODB_SETUP.md")

# Move data files
move_file("courses.json", "data/raw/courses.json")
move_file("unprocessed_courses.json", "data/raw/unprocessed_courses.json")
move_file("filtered_courses.json", "data/processed/filtered_courses.json")
move_file("skilled_occupations.json", "data/processed/skilled_occupations.json")
move_file(
    "courses_with_missing_details.json",
    "data/processed/courses_with_missing_details.json",
)

# Move main scripts
move_file("main.py", "src/main.py")
move_file("run_full_process.py", "src/run_full_process.py")
move_file("cleanup.py", "src/cleanup.py")

# Move configuration files
move_file("requirements.txt", "requirements.txt")
move_file("setup.bat", "setup.bat")
move_file("setup.sh", "setup.sh")
move_file("README.md", "README.md")
move_file("LICENSE", "LICENSE")

# Remove unnecessary files
unnecessary_files = [
    "response.html",
    "__pycache__",
    "scrapy.cfg",
    "settings.py",
    "run_spider.py",
]

for file in unnecessary_files:
    try:
        if os.path.isdir(file):
            shutil.rmtree(file)
        else:
            os.remove(file)
        print(f"Removed {file}")
    except Exception as e:
        print(f"Error removing {file}: {str(e)}")
