# QUT Course Scraper 🚀

## Overview

This project automatically pulls course and unit data from QUT using Scrapy and stores it in MongoDB. The setup includes all necessary dependencies for quick installation.

## 1. Install Python Windows

1. Download Python from the official site: [Python Downloads](https://www.python.org/downloads/)
2. Run the installer and check the box for "Add Python to PATH" before installing.
3. Verify installation:  
   `python --version`

## 2. Install Python Linux/MacOS

Most Linux and MacOS will come with python pre-installed.

#### To Check:

`python3 --version  `

### Debian/Ubuntu

```
sudo apt update
sudo apt install python3 python3-pip
```

### MacOS

```
brew install python
```

### Verify Installation:

`python3 --version`

## Setup Instructions

1. Clone the Repository

```
git clone https://github.com/TiuDepZai/qut-course-scraper.git
cd qut-course-scraper
```

2. Install Dependencies

#### Windows

```
pip install -r requirements.txt
```

#### Linux/MacOS

```
python3 -m pip install -r requirements.txt
```

3. MongoDB Setup

### Windows

#### Download MongoDB

[MongoDB Downloads](https://www.mongodb.com/try/download/community)
Install and start MongoDB  
`net start MongoDB`

### Linux/macOS

#### Debian/Ubuntu

```
sudo apt update
sudo apt install -y mongodb
sudo systemctl start mongod
```

### MacOS (Homebrew users)

```
brew tap mongodb/brew
brew install mongodb-community@6.0
brew services start mongodb-community@6.0
```

#### Check MongoDB status:

`mongod --version`

## Running the Scraper

### Course Data

1. Run the main script to scrape course data:
   `python src/main.py`

The scraper will:

- Create necessary directories for raw and processed data
- Fetch course information from QUT's website
- Process and store course details
- Handle errors and log any issues
- Save data temporarily as JSON files

2. Import data to MongoDB:
   `python src/database/mongodb/import_to_mongodb.py`

This will:

- Connect to your local MongoDB instance
- Create a database named `qut_courses`
- Create collections for courses, course details, and unprocessed courses
- Import all scraped data into the appropriate collections
- Create indexes for better query performance

3. Verify the data import:
   `python src/database/mongodb/show_mongodb_data.py`

This will display:

- Total number of courses imported
- Total number of course details
- Total number of unprocessed courses
- Sample data from each collection

4. Clean up temporary files:
   `python src/cleanup.py`

### Skilled Occupation Data

1. Run the occupation scraper:
   `python src/occupations/occupation_scraper.py`

This will:

- Scrape skilled occupation codes from the Department of Home Affairs website
- Save the data to a JSON file in `src/occupations/data/raw/occupations.json`
- Include occupation codes, titles, skill levels, and assessing authorities

2. Import occupation data to MongoDB:
   `python src/occupations/database/mongodb/import_occupations.py`

This will:

- Import the occupation data into the `occupations` collection
- Create indexes for efficient querying
- Store metadata about the scraping process

3. View occupation data:
   `python src/occupations/database/mongodb/show_occupations.py`

This will display:

- Total number of occupations
- Source and date information
- Sample occupation data

## Database Structure

The MongoDB database (`qut_courses`) contains four collections:

1. `courses` - Basic information about all courses
2. `course_details` - Detailed information about each course
3. `not_courses` - Records of courses that couldn't be processed
4. `occupations` - Skilled occupation codes and related information

## Error Handling

- Failed scraping attempts are logged in `not_courses` collection
- Detailed error logs are available in the `logs` directory
- The system implements retry logic for failed requests

# Contributing

Feel free to submit issues or pull requests to improve this scraper.

# License

This project is open-source and available under the MIT License.
