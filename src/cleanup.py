import os
from pathlib import Path


def cleanup_json_files():
    # Get the project root directory
    PROJECT_ROOT = Path(__file__).parent.parent
    RAW_DIR = PROJECT_ROOT / "data" / "raw"

    # Count of files removed
    removed_count = 0

    # List all JSON files
    json_files = list(RAW_DIR.glob("*.json"))

    print(f"Found {len(json_files)} JSON files to remove")

    # Remove each JSON file
    for file_path in json_files:
        try:
            file_path.unlink()
            print(f"Removed: {file_path.name}")
            removed_count += 1
        except Exception as e:
            print(f"Error removing {file_path.name}: {e}")

    print(f"\nCleanup completed. Removed {removed_count} JSON files.")


if __name__ == "__main__":
    cleanup_json_files()
