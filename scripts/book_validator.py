import json
import os
from typing import Dict, List, Set
from pathlib import Path

# TODO: move MASTER_BOOKS to it's own file

# Master book list with OSIS codes and English names
MASTER_BOOKS = {
    "Gen": "Genesis",
    "Exod": "Exodus",
    "Lev": "Leviticus",
    "Num": "Numbers",
    "Deut": "Deuteronomy",
    "Josh": "Joshua",
    "Judg": "Judges",
    "Ruth": "Ruth",
    "1Sam": "1 Samuel",
    "2Sam": "2 Samuel",
    "1Kgs": "1 Kings",
    "2Kgs": "2 Kings",
    "1Chr": "1 Chronicles",
    "2Chr": "2 Chronicles",
    "Ezra": "Ezra",
    "Neh": "Nehemiah",
    "Tob": "Tobit",
    "Jdt": "Judith",
    "Esth": "Esther",
    "1Macc": "1 Maccabees",
    "2Macc": "2 Maccabees",
    "Job": "Job",
    "Ps": "Psalms",
    "Prov": "Proverbs",
    "Eccl": "Ecclesiastes",
    "Song": "Song of Songs",
    "Wis": "Wisdom",
    "Sir": "Sirach",
    "Isa": "Isaiah",
    "Jer": "Jeremiah",
    "Lam": "Lamentations",
    "Bar": "Baruch",
    "Ezek": "Ezekiel",
    "Dan": "Daniel",
    "Hos": "Hosea",
    "Joel": "Joel",
    "Amos": "Amos",
    "Obad": "Obadiah",
    "Jonah": "Jonah",
    "Mic": "Micah",
    "Nah": "Nahum",
    "Hab": "Habakkuk",
    "Zeph": "Zephaniah",
    "Hag": "Haggai",
    "Zech": "Zechariah",
    "Mal": "Malachi",
    "Matt": "Matthew",
    "Mark": "Mark",
    "Luke": "Luke",
    "John": "John",
    "Acts": "Acts",
    "Rom": "Romans",
    "1Cor": "1 Corinthians",
    "2Cor": "2 Corinthians",
    "Gal": "Galatians",
    "Eph": "Ephesians",
    "Phil": "Philippians",
    "Col": "Colossians",
    "1Thess": "1 Thessalonians",
    "2Thess": "2 Thessalonians",
    "1Tim": "1 Timothy",
    "2Tim": "2 Timothy",
    "Titus": "Titus",
    "Phlm": "Philemon",
    "Heb": "Hebrews",
    "Jas": "James",
    "1Pet": "1 Peter",
    "2Pet": "2 Peter",
    "1John": "1 John",
    "2John": "2 John",
    "3John": "3 John",
    "Jude": "Jude",
    "Rev": "Revelation"
}

def find_bible_json_files() -> List[str]:
    """
    Find all JSON files in the data directory.

    Returns:
        List[str]: List of paths to JSON files
    """
    data_dir = Path("data")
    if not data_dir.exists():
        print("Error: data directory does not exist")
        return []

    json_files = list(data_dir.glob("*.json"))
    if not json_files:
        print("Error: No JSON files found in data directory")
        return []

    return [str(f) for f in json_files]

def select_json_file(json_files: List[str]) -> str:
    """
    Let the user select a JSON file to validate.

    Args:
        json_files (List[str]): List of paths to JSON files

    Returns:
        str: Selected file path
    """
    print("\nAvailable Bible JSON files:")
    for i, file_path in enumerate(json_files, 1):
        print(f"{i}. {os.path.basename(file_path)}")

    while True:
        try:
            choice = input("\nSelect a file number to validate (or 'q' to quit): ")
            if choice.lower() == 'q':
                exit(0)

            index = int(choice) - 1
            if 0 <= index < len(json_files):
                return json_files[index]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")

def validate_bible_json(file_path: str) -> None:
    """
    Validate that all required books are present in the Bible JSON file.

    Args:
        file_path (str): Path to the Bible JSON file
    """
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        return

    try:
        # Load the Bible JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            bible_data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file")
        return
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return

    # Get sets of required and present books
    required_books = set(MASTER_BOOKS.keys())
    present_books = set(bible_data.keys())

    # Find missing books
    missing_books = required_books - present_books
    extra_books = present_books - required_books

    # Print results
    print(f"\nBible Book Validation Results for {os.path.basename(file_path)}")
    print("=" * 50)
    print(f"Total required books: {len(required_books)}")
    print(f"Total present books: {len(present_books)}")
    print(f"Missing books: {len(missing_books)}")
    print(f"Extra books: {len(extra_books)}")

    if missing_books:
        print("\nMissing Books:")
        for book_code in sorted(missing_books):
            print(f"  - {book_code} ({MASTER_BOOKS[book_code]})")

    if extra_books:
        print("\nExtra Books (not in master list):")
        for book_code in sorted(extra_books):
            print(f"  - {book_code}")

    # Validate book structure
    print("\nBook Structure Validation:")
    structure_errors = []
    for book_code, book_data in bible_data.items():
        if "title" not in book_data:
            structure_errors.append(f"  - {book_code}: Missing 'title' field")
        if "chapters" not in book_data:
            structure_errors.append(f"  - {book_code}: Missing 'chapters' field")
        elif not isinstance(book_data["chapters"], dict):
            structure_errors.append(f"  - {book_code}: 'chapters' is not a dictionary")

    if structure_errors:
        print("\nStructure Errors Found:")
        for error in structure_errors:
            print(error)
    else:
        print("  ✓ All books have correct structure")

    # Print final validation status
    if not missing_books and not extra_books and not structure_errors:
        print("\n✓ Validation passed: All required books are present with correct structure")
    else:
        print("\n✗ Validation failed: See issues above")

if __name__ == "__main__":
    # Find all JSON files in the data directory
    json_files = find_bible_json_files()
    if not json_files:
        exit(1)

    # Let user select a file to validate
    selected_file = select_json_file(json_files)
    validate_bible_json(selected_file)
