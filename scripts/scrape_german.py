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
    "apg": "Acts",
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

# Mapping of special characters in book codes to URL-safe versions
URL_MAP = {
    "Röm": "roem",
    "Apg": "apg",
    # Add other special character mappings if needed
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

                # Special handling for Kings books
                if book_code in ['1Kön', '2Kön']:
                    book_code = book_code.replace('Kön', 'Koen')



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
    # Convert book code to URL-safe version if needed
    url_book_code = URL_MAP.get(book_code, book_code.lower())
    url = f"{TABLE_OF_CONTENTS}{url_book_code}{chapter}.html"
    print(f"\nAttempting to fetch: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        print(f"Response status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return {}

    soup = BeautifulSoup(response.text, 'html.parser')
    verses = {}

    # Find all table rows that contain verses
    rows = soup.find_all('tr')
    print(f"Found {len(rows)} table rows")

    for row in rows:
        # Try to find verse cell with width attribute first (standard structure)
        verse_cell = row.find('td', width="10%")
        if not verse_cell:
            # If not found, try finding any td with an anchor (1 Chronicles structure)
            verse_cell = row.find('td')
            if not verse_cell or not verse_cell.find('a'):
                continue

        verse_link = verse_cell.find('a')
        if not verse_link:
            continue

        verse_id = verse_link.get('id')
        if not verse_id:
            continue

        try:
            verse_num = int(verse_id)
            print(f"Found verse {verse_num}")

            # Try to find text cell with width attribute first (standard structure)
            text_cell = row.find('td', width="75%")
            if not text_cell:
                # If not found, try finding the second td (1 Chronicles structure)
                text_cell = row.find_all('td')[1] if len(row.find_all('td')) > 1 else None

            if text_cell:
                # Clean up the text by removing newlines, extra whitespace, and forward slashes
                verse_text = ' '.join(text_cell.text.strip().replace('/', '').split())
                verses[verse_num] = verse_text
                print(f"  {book_code} {chapter}:{verse_num} - {verse_text}")
            else:
                print(f"  Warning: No text cell found for verse {verse_num}")
        except (ValueError, IndexError) as e:
            print(f"  Warning: Error processing verse: {e}")
            continue

    print(f"Total verses found: {len(verses)}")
    return verses

def print_detected_books(book_info: Dict[str, Tuple[str, int]]):
    """Print the list of detected books and their chapter counts."""
    print("\nDetected Books:")
    print("-" * 50)
    print(f"{'German Code':<10} {'English Code':<10} {'Title':<30} {'Chapters':<8}")
    print("-" * 50)

    for book_code, (title, chapters) in book_info.items():
        english_code = OSIS_MAP.get(book_code, "Unknown")
        print(f"{book_code:<10} {english_code:<10} {title[:30]:<30} {chapters:<8}")

    print("-" * 50)
    print(f"Total books detected: {len(book_info)}\n")

def scrape_bible(output_dir: str = "data"):
    """Scrape the entire German Bible and save after each book."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Get table of contents
    print("Getting table of contents...")
    book_info = get_table_of_contents()

    # Print detected books
    print_detected_books(book_info)

    # Initialize the Bible structure
    bible_data = {}
    output_file = os.path.join(output_dir, "bible_de.json")

    # Try to load existing data if file exists
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                bible_data = json.load(f)
            print("Loaded existing data from", output_file)
        except json.JSONDecodeError:
            print("Could not load existing data, starting fresh")

    # Scrape each book
    total_books = len(book_info)
    for i, (book_code, (book_title, max_chapter)) in enumerate(book_info.items(), 1):
        # Skip if we already have this book
        if OSIS_MAP[book_code] in bible_data:
            print(f"[{i}/{total_books}] Skipping {book_code} ({book_title}) - already scraped")
            continue

        print(f"[{i}/{total_books}] Scraping {book_code} ({book_title})...")
        book_data = {
            "title": book_title,
            "chapters": {}
        }

        # Scrape each chapter
        for chapter in range(1, max_chapter + 1):
            print(f"  Chapter {chapter}/{max_chapter}...")
            try:
                verses = get_chapter_text(book_code, chapter)
                if verses:
                    book_data["chapters"][str(chapter)] = verses
                time.sleep(1)  # Be nice to the server
            except Exception as e:
                print(f"Error scraping {book_code} {chapter}: {e}")
                continue

        # Add book data to Bible and save after each book
        if book_data["chapters"]:
            bible_data[OSIS_MAP[book_code]] = book_data
            # Save after each book
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(bible_data, f, ensure_ascii=False, indent=2)
            print(f"Saved {book_code} to {output_file}")
        else:
            print(f"Warning: No chapters found for {book_code}")

    print(f"Completed scraping all books. Final data saved to {output_file}")

if __name__ == "__main__":
    scrape_bible()




# looks like verses aren't being scraped from 1chr.

# 1chr verse structure:

# <tr>
#   <td>
#     <a id="1" href="#1" name="1"><strong>1 Chr 1,1</strong></a>
#   </td>
#   <td>Adam, Set, Enosch,</td> <!-- verse text -->
#   <td>&nbsp;</td>
# </tr>

# 2chr verse structure:

# <tr>
#   <td width="10%">
#     <a id="1" href="#1" name="1"><strong>2 Chr 1,1</strong></a>
#   </td>

#   <td width="75%">
#     Salomo, der Sohn Davids, gewann Macht in seinem Königtum, der Herr, sein
#     Gott, war mit ihm und ließ ihn überaus stark werden.
#   </td>

#   <td width="15%"></td>
# </tr>
