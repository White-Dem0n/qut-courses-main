import asyncio
import subprocess
import sys
import os
import time
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent


async def run_script(script_name):
    """Run a Python script and wait for it to complete."""
    print(f"\n{'='*80}")
    print(f"Running {script_name}...")
    print(f"{'='*80}")

    # Construct the full path to the script
    script_path = PROJECT_ROOT / "src" / script_name

    process = await asyncio.create_subprocess_exec(
        sys.executable,
        str(script_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        print(f"Script {script_name} completed successfully.")
        print(stdout.decode())
    else:
        print(f"Script {script_name} failed with error code {process.returncode}.")
        print(stderr.decode())

    return process.returncode


async def main():
    """Run the full process: extract data, import to MongoDB, and clean up."""
    start_time = time.time()

    # Step 1: Run the main script to extract all course information
    result = await run_script("main.py")
    if result != 0:
        print("Error extracting course information. Aborting.")
        return

    # Step 2: Import the data to MongoDB
    result = await run_script("database/mongodb/import_to_mongodb.py")
    if result != 0:
        print("Error importing data to MongoDB. Aborting.")
        return

    # Step 3: Clean up JSON files
    result = await run_script("cleanup.py")
    if result != 0:
        print("Error cleaning up JSON files. Aborting.")
        return

    end_time = time.time()
    duration = end_time - start_time

    print(f"\n{'='*80}")
    print(f"Full process completed in {duration:.2f} seconds.")
    print(f"{'='*80}")
    print(f"All course information has been extracted and saved to MongoDB.")
    print(f"JSON files have been cleaned up.")
    print(f"{'='*80}")


if __name__ == "__main__":
    asyncio.run(main())
