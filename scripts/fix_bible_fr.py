import json
import re
import os
import argparse

def clean_verse_text(text):
    """Remove parenthetical verse numbers from the verse text."""
    # Remove patterns like (1:11), (65:12), etc.
    return re.sub(r'\(\d+:\d+\)\s*', '', text)

def clean_bible_data(bible_data):
    """Clean all verses in the Bible data."""
    cleaned_data = {}

    for book_code, book_data in bible_data.items():
        cleaned_book = {
            "title": book_data["title"],
            "chapters": {}
        }

        for chapter_num, chapter_data in book_data["chapters"].items():
            cleaned_chapter = {}

            for verse_num, verse_text in chapter_data.items():
                cleaned_verse = clean_verse_text(verse_text)
                cleaned_chapter[verse_num] = cleaned_verse

            cleaned_book["chapters"][chapter_num] = cleaned_chapter

        cleaned_data[book_code] = cleaned_book

    return cleaned_data

def main():
    parser = argparse.ArgumentParser(description='Clean French Bible data by removing parenthetical verse numbers.')
    parser.add_argument('--input', type=str, default='data/bible_fr_toclean.json',
                        help='Input JSON file path (default: data/bible_fr_toclean.json)')
    parser.add_argument('--output', type=str, default='data/bible_fr.json',
                        help='Output JSON file path (default: data/bible_fr.json)')
    args = parser.parse_args()

    # Ensure input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist")
        return

    # Load the input data
    print(f"Loading data from {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        bible_data = json.load(f)

    # Clean the data
    print("Cleaning verse text...")
    cleaned_data = clean_bible_data(bible_data)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Save the cleaned data
    print(f"Saving cleaned data to {args.output}")
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=2)

    print("Done!")

if __name__ == "__main__":
    main()

# Usage:
# python3 scripts/fix_bible_fr.py --input data/bible_fr_toclean.json --output data/bible_fr.json




