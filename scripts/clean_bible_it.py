import json
import re
from pathlib import Path

def clean_verse_text(text):
    # Remove markers in format [number][lowercaseletter]
    return re.sub(r'\[\d+[a-z]\]', '', text)

def clean_bible_json(input_path, output_path):
    # Read the input JSON file
    with open(input_path, 'r', encoding='utf-8') as f:
        bible_data = json.load(f)

    # Process each book, chapter, and verse
    for book in bible_data.values():
        if 'chapters' in book:
            for chapter in book['chapters'].values():
                for verse_num, verse_text in chapter.items():
                    chapter[verse_num] = clean_verse_text(verse_text)

    # Write the cleaned data to a new file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(bible_data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    # Define paths
    data_dir = Path(__file__).parent.parent / 'data'
    input_file = data_dir / 'bible_it_toclean.json'
    output_file = data_dir / 'bible_it_clean.json'

    # Clean the JSON file
    clean_bible_json(input_file, output_file)
    print(f"Cleaned Bible data has been saved to {output_file}")
