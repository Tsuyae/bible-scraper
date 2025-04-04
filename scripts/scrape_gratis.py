# a script to scrape the gratis bible website:
# https://gratis.bible/fr/dejer/

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from typing import Dict, List, Optional

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

bible_dictionary = [
    "Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth", "1Sam", "2Sam",
    "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh", "Esth", "Job", "Ps", "Prov",
    "Eccl", "Song", "Isa", "Jer", "Lam", "Ezek", "Dan", "Hos", "Joel", "Amos",
    "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag", "Zech", "Mal", "Matt",
    "Mark", "Luke", "John", "Acts", "Rom", "1Cor", "2Cor", "Gal", "Eph", "Phil",
    "Col", "1Thess", "2Thess", "1Tim", "2Tim", "Titus", "Phlm", "Heb", "Jas",
    "1Pet", "2Pet", "1John", "2John", "3John", "Jude", "Rev", "Tob", "Jdt", "Wis",
    "Sir", "Bar", "1Macc", "2Macc"
]

def load_existing_data(file_path: str) -> Dict:
    """Load existing data from JSON file if it exists."""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_progress(file_path: str, data: Dict):
    """Save data to JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_book_chapters(book_slug: str) -> List[str]:
    """Get all chapter numbers for a given book."""
    url = f"https://gratis.bible/fr/dejer/{book_slug}/"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    chapter_list = soup.find('ul')
    if not chapter_list:
        return []

    chapters = []
    for link in chapter_list.find_all('a'):
        # Extract chapter number from href (e.g., "/fr/dejer/gen/1" -> "1")
        chapter_num = link['href'].split('/')[-1]
        chapters.append(chapter_num)

    return sorted(chapters, key=int)

def get_book_title(book_slug: str) -> Optional[str]:
    """Get the localized title of a book."""
    url = f"https://gratis.bible/fr/dejer/{book_slug}/"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    title_tag = soup.find('strong')
    return title_tag.text if title_tag else None

def get_chapter_verses(book_slug: str, chapter_num: str) -> Dict[str, str]:
    """Get all verses for a given chapter."""
    url = f"https://gratis.bible/fr/dejer/{book_slug}/{chapter_num}/"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    verses = {}

    # Find all verse spans
    verse_spans = soup.find_all('span', class_='verse')
    for span in verse_spans:
        # Get verse number from the anchor tag
        verse_num = span.find('a')['name']
        # Get verse text (everything after the verse number)
        verse_text = span.get_text().lstrip(verse_num).strip()
        verses[verse_num] = verse_text

    return verses

def scrape_bible():
    """Main function to scrape the entire Bible."""
    output_path = os.path.join('data', 'bible_fr.json')
    bible_data = load_existing_data(output_path)

    for book_code in bible_dictionary:
        # Skip if book is already scraped
        if book_code in bible_data:
            print(f"Skipping {book_code} (already scraped)...")
            continue

        print(f"Scraping {book_code}...")

        # Get book title and chapters
        book_slug = book_code.lower()
        title = get_book_title(book_slug)
        if not title:
            print(f"Warning: Could not find title for {book_code}")
            continue

        chapters = get_book_chapters(book_slug)
        if not chapters:
            print(f"Warning: No chapters found for {book_code}")
            continue

        # Initialize book data
        bible_data[book_code] = {
            "title": title,
            "chapters": {}
        }

        # Scrape each chapter
        for chapter_num in chapters:
            print(f"  Scraping chapter {chapter_num}...")
            verses = get_chapter_verses(book_slug, chapter_num)
            bible_data[book_code]["chapters"][chapter_num] = verses

            # Add a small delay to be nice to the server
            time.sleep(0.5)

        # Save progress after each book
        save_progress(output_path, bible_data)
        print(f"Completed and saved {book_code}")

    return bible_data

if __name__ == "__main__":
    try:
        bible_data = scrape_bible()
        print("Scraping completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

