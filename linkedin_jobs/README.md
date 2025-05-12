# LinkedIn Job Scraper

A Scrapy-based web scraper for collecting IT job listings from LinkedIn. This project focuses on gathering information about IT jobs and internships in Australia.

## Features

- Scrapes IT job listings from LinkedIn
- Focuses on Australian job market
- Collects detailed job information including:
  - Job title and company
  - Location and job type
  - Experience level
  - Required skills and technologies
  - Salary information
  - Remote work options
  - Visa sponsorship availability
- Generates statistics about job market trends
- Respects LinkedIn's rate limits and robots.txt
- Implements anti-detection measures

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Navigate to the project directory:

   ```bash
   cd linkedin_jobs
   ```

2. Run the spider:
   ```bash
   scrapy crawl linkedin_jobs
   ```

The spider will:

- Search for IT jobs in major Australian cities
- Collect job details from LinkedIn
- Save results to JSON files in the `data` directory
- Generate statistics about the job market

## Output

The spider generates two types of output files:

1. Job listings (`linkedin_jobs_YYYYMMDD_HHMMSS.json`):

   - Contains detailed information about each job
   - Includes job descriptions, requirements, and company information

2. Statistics (`job_stats_YYYYMMDD_HHMMSS.json`):
   - Total number of jobs found
   - Distribution by location
   - Distribution by role type
   - Distribution by experience level
   - Most common technologies

## Configuration

You can modify the following settings in `settings.py`:

- Search keywords
- Target locations
- Experience levels
- Rate limiting parameters
- Output format

## Important Notes

- This scraper is for educational purposes only
- Respect LinkedIn's terms of service
- Implement proper rate limiting
- Do not overload LinkedIn's servers
- Consider using LinkedIn's official API when available

## Legal Disclaimer

This project is for educational purposes only. Users are responsible for ensuring their use of this tool complies with LinkedIn's terms of service and applicable laws. The developers are not responsible for any misuse or legal issues arising from the use of this tool.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
