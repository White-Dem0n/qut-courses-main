# MongoDB Setup for QUT Courses Data

This guide will help you set up MongoDB and import the QUT courses data into a structured database.

## Installing MongoDB

### Windows
1. Download MongoDB Community Server from [MongoDB Download Center](https://www.mongodb.com/try/download/community)
2. Run the installer and follow the installation wizard
3. Choose "Complete" installation type
4. Install MongoDB Compass (the GUI tool) when prompted
5. Complete the installation

### macOS
Using Homebrew:
```
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### Linux (Ubuntu)
```
sudo apt update
sudo apt install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

## Verifying MongoDB Installation

After installation, verify that MongoDB is running:

### Windows
```
net start MongoDB
```

### macOS/Linux
```
mongod --version
```

## Running the Import Script

1. Make sure MongoDB is running
2. Activate your virtual environment:
   ```
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```
3. Run the import script:
   ```
   python import_to_mongodb.py
   ```

## Database Structure

The script creates a MongoDB database called `qut_courses` with the following collections:

1. **courses**: Contains the list of all courses from QUT
   - Document structure:
     ```json
     {
       "courseCode": "AB05",
       "course_title": "Bachelor of Architectural Design"
     }
     ```

2. **course_details**: Contains detailed information about each course
   - Document structure:
     ```json
     {
       "course_name": "Bachelor of Architectural Design",
       "course_code": "AB05",
       "identifier": "43358",
       "durations": [...],
       "delivery_location": "Gardens Point",
       "atar_rank": "80.00",
       "qtac_code": "412301",
       "cricos_code": "113183D",
       "main_description": "...",
       "details_and_units": [...],
       "highlights": [...],
       "what_to_expect-careers_and_outcome": {...},
       "url": "https://www.qut.edu.au/courses/bachelor-of-architectural-design",
       "day_obtained": "2025-04-10",
       "import_date": "2025-04-10 12:00:00"
     }
     ```

3. **not_courses**: Contains information about courses that couldn't be processed
   - Document structure:
     ```json
     {
       "url": "https://www.qut.edu.au/courses/bachelor-of-business",
       "error": "Course code is missing",
       "import_date": "2025-04-10 12:00:00"
     }
     ```

## Querying the Database

You can use MongoDB Compass or the MongoDB shell to query the database:

### Using MongoDB Compass
1. Open MongoDB Compass
2. Connect to `mongodb://localhost:27017`
3. Navigate to the `qut_courses` database
4. Select a collection and use the query interface

### Using MongoDB Shell
```
# Connect to MongoDB shell
mongosh

# Switch to the qut_courses database
use qut_courses

# Query all courses
db.courses.find()

# Find a specific course by code
db.courses.find({courseCode: "AB05"})

# Find courses with ATAR rank above 80
db.course_details.find({atar_rank: {$gt: "80.00"}})
```

## Troubleshooting

If you encounter issues with the import script:

1. Make sure MongoDB is running
2. Check that the JSON files exist in the current directory
3. Verify that you have the pymongo package installed:
   ```
   pip install pymongo
   ```
4. Check the error messages for specific issues 