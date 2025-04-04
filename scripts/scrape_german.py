import requests
from bs4 import BeautifulSoup
import json
import os
from typing import Dict, List, Optional, Tuple
import time

TABLE_OF_CONTENTS = "https://www.uibk.ac.at/theol/leseraum/bibel/"

# Mapping of German OSIS codes to English OSIS codes
OSIS_MAP = {
    "Gen": "Gen",
    "Ex": "Exod",
    "Lev": "Lev",
    "Num": "Num",
    "Dtn": "Deut",
    "Jos": "Josh",
    "Ri": "Judg",
    "Rut": "Ruth",
    "1Sam": "1Sam",
    "2Sam": "2Sam",
    "1Koen": "1Kgs",
    "2Koen": "2Kgs",
    "1Chr": "1Chr",
    "2Chr": "2Chr",
    "Esra": "Ezra",
    "Neh": "Neh",
    "Tob": "Tob",
    "Jdt": "Jdt",
    "Est": "Esth",
    "1Makk": "1Macc",
    "2Makk": "2Macc",
    "Ijob": "Job",
    "Ps": "Ps",
    "Spr": "Prov",
    "Koh": "Eccl",
    "Hld": "Song",
    "Weish": "Wis",
    "Sir": "Sir",
    "Jes": "Isa",
    "Jer": "Jer",
    "Klgl": "Lam",
    "Bar": "Bar",
    "Ez": "Ezek",
    "Dan": "Dan",
    "Hos": "Hos",
    "Joel": "Joel",
    "Am": "Amos",
    "Obd": "Obad",
    "Jona": "Jonah",
    "Mi": "Mic",
    "Nah": "Nah",
    "Hab": "Hab",
    "Zef": "Zeph",
    "Hag": "Hag",
    "Sach": "Zech",
    "Mal": "Mal",
    "Mt": "Matt",
    "Mk": "Mark",
    "Lk": "Luke",
    "Joh": "John",
    "Apg": "Acts",
    "Röm": "Rom",
    "1Kor": "1Cor",
    "2Kor": "2Cor",
    "Gal": "Gal",
    "Eph": "Eph",
    "Phil": "Phil",
    "Kol": "Col",
    "1Thess": "1Thess",
    "2Thess": "2Thess",
    "1Tim": "1Tim",
    "2Tim": "2Tim",
    "Tit": "Titus",
    "Phlm": "Phlm",
    "Hebr": "Heb",
    "Jak": "Jas",
    "1Petr": "1Pet",
    "2Petr": "2Pet",
    "1Joh": "1John",
    "2Joh": "2John",
    "3Joh": "3John",
    "Jud": "Jude",
    "Offb": "Rev"
}

def get_table_of_contents() -> Dict[str, Tuple[str, int]]:
    """Get the table of contents and return a dictionary mapping book codes to their titles and max chapter numbers."""
    response = requests.get(TABLE_OF_CONTENTS)
    soup = BeautifulSoup(response.text, 'html.parser')

    book_info = {}

    # Find all table rows in the table of contents
    rows = soup.find_all('tr')
    for row in rows:
        # Get the book code and chapter links
        cells = row.find_all('td')
        if len(cells) >= 3:
            book_link = cells[0].find('a')
            book_code_link = cells[1].find('a')
            if book_link and book_code_link:
                book_title = book_link.text.strip()
                book_code = book_code_link.text.strip()
                if book_code in OSIS_MAP:
                    # Get all chapter links
                    chapter_links = cells[2].find_all('a')
                    if chapter_links:
                        # Get the last chapter number
                        last_chapter = int(chapter_links[-1].text.strip())
                        book_info[book_code] = (book_title, last_chapter)

    return book_info

def get_chapter_text(book_code: str, chapter: int) -> Dict[int, str]:
    """Get the text for a specific chapter."""
    url = f"{TABLE_OF_CONTENTS}{book_code.lower()}{chapter}.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    verses = {}

    # Find all table rows that contain verses
    rows = soup.find_all('tr')
    for row in rows:
        # Check if this row contains a verse
        verse_cell = row.find('td', width="10%")
        if verse_cell and verse_cell.find('a'):
            verse_link = verse_cell.find('a')
            if verse_link and verse_link.get('id'):
                try:
                    verse_num = int(verse_link['id'])
                    # Get the verse text from the next cell
                    text_cell = row.find('td', width="75%")
                    if text_cell:
                        verse_text = text_cell.text.strip()
                        verses[verse_num] = verse_text
                except ValueError:
                    continue

    return verses

def scrape_bible(output_dir: str = "data"):
    """Scrape Genesis and save it to a JSON file."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get table of contents
    print("Getting table of contents...")
    book_info = get_table_of_contents()

    # Initialize the Bible structure
    bible_data = {}

    # Only scrape Genesis
    if "Gen" in book_info:
        book_title, max_chapter = book_info["Gen"]
        print(f"Scraping Genesis ({book_title})...")
        book_data = {
            "title": book_title,
            "chapters": {}
        }

        # Scrape each chapter
        for chapter in range(1, max_chapter + 1):
            print(f"  Chapter {chapter}...")
            try:
                verses = get_chapter_text("Gen", chapter)
                if verses:
                    book_data["chapters"][str(chapter)] = verses
                time.sleep(1)  # Be nice to the server
            except Exception as e:
                print(f"Error scraping Genesis {chapter}: {e}")
                continue

        # Add Genesis data to Bible
        if book_data["chapters"]:
            bible_data["Gen"] = book_data

    # Save Bible data
    output_file = os.path.join(output_dir, "german_bible.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(bible_data, f, ensure_ascii=False, indent=2)
    print(f"Saved Genesis to {output_file}")

if __name__ == "__main__":
    scrape_bible()
