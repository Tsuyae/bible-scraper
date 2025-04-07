import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Set

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

def validate_book_structure(book_data: Dict) -> List[str]:
    """Validate the structure of a single book."""
    errors = []

    # Check required fields
    if "title" not in book_data:
        errors.append("Missing 'title' field")
    if "chapters" not in book_data:
        errors.append("Missing 'chapters' field")
        return errors

    # Validate chapters structure
    chapters = book_data["chapters"]
    if not isinstance(chapters, dict):
        errors.append("'chapters' must be an object")
        return errors

    for chapter_num, chapter_data in chapters.items():
        if not isinstance(chapter_data, dict):
            errors.append(f"Chapter {chapter_num} must be an object")
            continue

        for verse_num, verse_text in chapter_data.items():
            if not isinstance(verse_text, str):
                errors.append(f"Verse {chapter_num}:{verse_num} must be a string")

    return errors

def compare_verses(master_data: Dict, test_data: Dict) -> Dict[str, Dict[str, Set[int]]]:
    """Compare verse counts between master and test data."""
    differences = {}

    for book_code in MASTER_BOOKS:
        if book_code not in master_data or book_code not in test_data:
            continue

        master_book = master_data[book_code]
        test_book = test_data[book_code]

        if "chapters" not in master_book or "chapters" not in test_book:
            continue

        master_chapters = master_book["chapters"]
        test_chapters = test_book["chapters"]

        for chapter_num in master_chapters:
            if chapter_num not in test_chapters:
                continue

            master_verses = set(master_chapters[chapter_num].keys())
            test_verses = set(test_chapters[chapter_num].keys())

            if master_verses != test_verses:
                if book_code not in differences:
                    differences[book_code] = {}
                differences[book_code][chapter_num] = {
                    "missing": master_verses - test_verses,
                    "extra": test_verses - master_verses
                }

    return differences

def compare_counts(master_data: Dict, test_data: Dict) -> Dict[str, Dict[str, int]]:
    """Compare chapter and verse counts between master and test data."""
    differences = {}

    for book_code in MASTER_BOOKS:
        if book_code not in master_data or book_code not in test_data:
            continue

        master_book = master_data[book_code]
        test_book = test_data[book_code]

        if "chapters" not in master_book or "chapters" not in test_book:
            continue

        master_chapters = master_book["chapters"]
        test_chapters = test_book["chapters"]

        # Compare chapter counts
        master_chapter_count = len(master_chapters)
        test_chapter_count = len(test_chapters)

        # Compare verse counts
        master_verse_count = sum(len(chapter) for chapter in master_chapters.values())
        test_verse_count = sum(len(chapter) for chapter in test_chapters.values())

        if master_chapter_count != test_chapter_count or master_verse_count != test_verse_count:
            differences[book_code] = {
                "master_chapters": master_chapter_count,
                "test_chapters": test_chapter_count,
                "master_verses": master_verse_count,
                "test_verses": test_verse_count
            }

    return differences

def get_available_bibles() -> List[str]:
    """Get list of available Bible JSON files in the data directory."""
    data_dir = Path(__file__).parent.parent / "data"
    if not data_dir.exists():
        return []

    return sorted([f.name for f in data_dir.glob("*.json")])

def select_file(files: List[str]) -> Optional[str]:
    """Simple interactive file selection."""
    if not files:
        return None

    print("\nAvailable Bible files:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")

    while True:
        try:
            choice = input("\nSelect a file number (or press Enter to cancel): ")
            if not choice:
                return None
            idx = int(choice) - 1
            if 0 <= idx < len(files):
                return files[idx]
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")

def main():
    # Get available Bible files
    available_bibles = get_available_bibles()
    if not available_bibles:
        print("No Bible JSON files found in the data directory.")
        return

    # Interactive file selection
    selected_file = select_file(available_bibles)
    if not selected_file:
        return

    file_path = Path(__file__).parent.parent / "data" / selected_file

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON file - {str(e)}")
        return
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return

    # Check for missing books
    missing_books = set(MASTER_BOOKS.keys()) - set(data.keys())
    if missing_books:
        print(f"\nFound {len(missing_books)} missing books:")
        for book in sorted(missing_books):
            print(f"  - {book} ({MASTER_BOOKS[book]})")

    # Validate structure of each book
    structure_errors = {}
    for book_code, book_data in data.items():
        errors = validate_book_structure(book_data)
        if errors:
            structure_errors[book_code] = errors

    if structure_errors:
        print("\nStructure errors:")
        for book_code, errors in structure_errors.items():
            print(f"\n{book_code}:")
            for error in errors:
                print(f"  - {error}")

    # Try to load master data for comparison
    master_path = Path(__file__).parent.parent / "data" / "bible_master.json"
    if master_path.exists():
        try:
            with open(master_path, 'r', encoding='utf-8') as f:
                master_data = json.load(f)

            # Compare counts
            count_differences = compare_counts(master_data, data)
            if count_differences:
                print("\nChapter and verse count differences:")
                for book_code, counts in count_differences.items():
                    print(f"\n{book_code}:")
                    if counts["master_chapters"] != counts["test_chapters"]:
                        print(f"  Chapters: Master={counts['master_chapters']}, Test={counts['test_chapters']}")
                    if counts["master_verses"] != counts["test_verses"]:
                        print(f"  Verses: Master={counts['master_verses']}, Test={counts['test_verses']}")

            # Compare individual verses
            differences = compare_verses(master_data, data)
            if differences:
                print("\nVerse differences:")
                for book_code, chapters in differences.items():
                    print(f"\n{book_code}:")
                    for chapter_num, diff in chapters.items():
                        if diff["missing"]:
                            print(f"  Chapter {chapter_num} - Missing verses: {sorted(diff['missing'])}")
                        if diff["extra"]:
                            print(f"  Chapter {chapter_num} - Extra verses: {sorted(diff['extra'])}")
        except Exception as e:
            print(f"\nWarning: Could not compare with master file - {str(e)}")

    if not missing_books and not structure_errors:
        print("\nValidation successful! All books present and structure is correct.")
    else:
        print("\nValidation completed with errors.")

if __name__ == '__main__':
    main()
