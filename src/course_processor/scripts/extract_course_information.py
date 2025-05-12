# The purpose of this script is to pull information from the each course information.
import sys
import re
import subprocess

if __name__ == "__main__":
    # Access arguments passed to the script
    course_code = sys.argv[1]  # First argument
    course_title = sys.argv[2]  # Second argument

    # Format the course title for the URL
    formatted_course_title = course_title.lower().replace(" ", "-")
    formatted_course_title = re.sub(
        r"-{2,}", "-", formatted_course_title
    )  # Remove extra dashes
    formatted_course_title = re.sub(
        r"[()]", "", formatted_course_title
    )  # Remove parentheses

    courseLink = f"https://www.qut.edu.au/courses/{formatted_course_title}"

    print(f"Processing course: {course_code} - {courseLink}")

    # Call the ECI.py script with the same arguments
    subprocess.run([sys.executable, "scripts/ECI.py", course_code, course_title])
