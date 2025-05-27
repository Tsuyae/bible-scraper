import os
import re
import json
import requests
from bs4 import BeautifulSoup
import html
import time
import argparse

# transferred from https://github.com/LongbeardCreative/bible-scraper

# Base URL for the Vatican website
BASE_URL = "https://www.vatican.va/archive/ESL0506/"

# Dictionary mapping Spanish book names to standardized OSIS abbreviations
BOOK_MAPPING = {
    "GENESIS": "Gen",
    "EXODO": "Exod",
    "LEVITICO": "Lev",
    "NUMEROS": "Num",
    "DEUTERONOMIO": "Deut",
    "JOSUE": "Josh",
    "JUECES": "Judg",
    "RUT": "Ruth",
    "PRIMER LIBRO DE SAMUEL": "1Sam",
    "SEGUNDO LIBRO DE SAMUEL": "2Sam",
    "PRIMER LIBRO DE LOS REYES": "1Kgs",
    "SEGUNDO LIBRO DE LOS REYES": "2Kgs",
    "PRIMER LIBRO DE LAS CRONICAS": "1Chr",
    "SEGUNDO LIBRO DE LAS CRONICAS": "2Chr",
    "ESDRAS": "Ezra",
    "NEHEMIAS": "Neh",
    "ESTER": "Esth",
    "JOB": "Job",
    "SALMOS": "Ps",
    "PROVERBIOS": "Prov",
    "ECLESIASTES": "Eccl",
    "CANTAR DE LOS CANTARES": "Song",
    "ISAIAS": "Isa",
    "JEREMIAS": "Jer",
    "LAMENTACIONES": "Lam",
    "EZEQUIEL": "Ezek",
    "DANIEL": "Dan",
    "OSEAS": "Hos",
    "JOEL": "Joel",
    "AMOS": "Amos",
    "ABDIAS": "Obad",
    "JONAS": "Jonah",
    "MIQUEAS": "Mic",
    "NAHUM": "Nah",
    "HABACUC": "Hab",
    "SOFONIAS": "Zeph",
    "AGEO": "Hag",
    "ZACARIAS": "Zech",
    "MALAQUIAS": "Mal",
    "EVANGELIO SEGUN SAN MATEO": "Matt",
    "EVANGELIO SEGUN SAN MARCOS": "Mark",
    "EVANGELIO SEGUN SAN LUCAS": "Luke",
    "EVANGELIO SEGUN SAN JUAN": "John",
    "HECHOS DE LOS APOSTOLES": "Acts",
    "CARTA A LOS ROMANOS": "Rom",
    "PRIMERA CARTA A LOS CORINTIOS": "1Cor",
    "SEGUNDA CARTA A LOS CORINTIOS": "2Cor",
    "CARTA A LOS GALATAS": "Gal",
    "CARTA A LOS EFESIOS": "Eph",
    "CARTA A LOS FILIPENSES": "Phil",
    "CARTA A LOS COLOSENSES": "Col",
    "PRIMERA CARTA A LOS TESALONICENSES": "1Thess",
    "SEGUNDA CARTA A LOS TESALONICENSES": "2Thess",
    "PRIMERA CARTA A TIMOTEO": "1Tim",
    "SEGUNDA CARTA A TIMOTEO": "2Tim",
    "CARTA A TITO": "Titus",
    "CARTA A FILEMON": "Phlm",
    "CARTA A LOS HEBREOS": "Heb",
    "CARTA DE SANTIAGO": "Jas",
    "PRIMERA CARTA DE SAN PEDRO": "1Pet",
    "SEGUNDA CARTA DE SAN PEDRO": "2Pet",
    "PRIMERA CARTA DE SAN JUAN": "1John",
    "SEGUNDA CARTA DE SAN JUAN": "2John",
    "TERCERA CARTA DE SAN JUAN": "3John",
    "CARTA DE SAN JUDAS": "Jude",
    "APOCALIPSIS": "Rev",
    # Apocrypha
    "TOBIAS": "Tob",
    "JUDIT": "Jdt",
    "BARUC": "Bar",
    "CARTA DE JEREMIAS": "EpJer",
    "PRIMER LIBRO DE LOS MACABEOS": "1Macc",
    "SEGUNDO LIBRO DE LOS MACABEOS": "2Macc",
    "SABIDURIA": "Wis",
    "ECLESIASTICO": "Sir",
    "DANIEL SUPLEMENTOS GRIEGOS": "AddDan",
    "ESTER SUPLEMENTOS GRIEGOS": "AddEsth"
}

# Dictionary of books with unique HTML formatting
ONE_PAGE_BOOKS = {
    "2John": {
        "url": "__P10U.HTM",
        "title": "SEGUNDA CARTA DE SAN JUAN"
    },
    "3John": {
        "url": "__P10V.HTM",
        "title": "TERCERA CARTA DE SAN JUAN"
    },
    "Obad": {
        "url": "__PF2.HTM",
        "title": "ABDIAS"
    },
    "Phlm": {
        "url": "__PZY.HTM",
        "title": "CARTA A FILEMON"
    },
    "Jude": {
        "url": "__P10W.HTM",
        "title": "CARTA DE SAN JUDAS"
    }
}

def get_html(url):
    """Fetch the HTML content of a URL with retries and error handling."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            if attempt < max_retries - 1:
                sleep_time = 2 ** attempt  # Exponential backoff
                print(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                print(f"Failed to fetch {url} after {max_retries} attempts")
                return None

def extract_verses(html_content):
    """Extract verse numbers and text from the HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all paragraph elements that contain verses
    verse_paragraphs = soup.find_all('p', class_='MsoNormal')

    verses = {}
    current_verse_number = None
    current_verse_text = []

    for p in verse_paragraphs:
        # Convert the paragraph to string and decode HTML entities
        p_str = str(p)

        # Check if this paragraph contains a verse number
        verse_match = re.search(r'>(\d+)\s', p_str)

        if verse_match:
            # If we were building a verse, save it before starting a new one
            if current_verse_number is not None and current_verse_text:
                verse_text = ' '.join(current_verse_text)
                verse_text = re.sub(r'\s+', ' ', verse_text).strip()
                verses[current_verse_number] = verse_text
                current_verse_text = []

            # Start a new verse
            current_verse_number = verse_match.group(1)
            text = p.get_text(strip=True)
            # Remove the verse number from the beginning
            text = re.sub(r'^\s*' + current_verse_number + r'\s*', '', text)
            current_verse_text.append(text)
        elif current_verse_number is not None:
            # This is a continuation of the current verse
            text = p.get_text(strip=True)
            current_verse_text.append(text)

    # Don't forget to save the last verse
    if current_verse_number is not None and current_verse_text:
        verse_text = ' '.join(current_verse_text)
        verse_text = re.sub(r'\s+', ' ', verse_text).strip()
        verses[current_verse_number] = verse_text

    # Decode HTML entities for all verses
    for verse_number in verses:
        verses[verse_number] = html.unescape(verses[verse_number])

    return verses

def extract_book_info(html_content):
    """Extract book name and chapter number from the meta tag."""
    soup = BeautifulSoup(html_content, 'html.parser')
    part_meta = soup.find('meta', {'name': 'part'})

    if part_meta and 'content' in part_meta.attrs:
        content = part_meta['content']
        parts = content.split('>')

        if len(parts) >= 3:
            book_name = parts[1].strip()
            chapter_number = parts[2].strip()
            return book_name, chapter_number

    return None, None

def scrape_chapter(url):
    """Scrape a single chapter's verses and metadata."""
    html_content = get_html(url)
    if not html_content:
        return None, None, None

    book_name, chapter_number = extract_book_info(html_content)
    verses = extract_verses(html_content)

    return book_name, chapter_number, verses

def load_existing_bible_data(file_path):
    """Load existing Bible data from a JSON file if it exists."""
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error loading {file_path}. Starting with empty data.")
    return {}

def scrape_bible(limit=None, existing_data=None, book_osis=None):
    """Scrape the entire Bible and structure it as JSON.

    Args:
        limit (int, optional): Maximum number of chapters to scrape. Useful for testing.
        existing_data (dict, optional): Existing Bible data to avoid re-scraping.
        book_osis (str, optional): OSIS code of a single book to scrape (e.g., "Jude").
    """
    # Initialize with existing data if provided
    bible_data = existing_data or {}

    # If a specific book is requested, check if it's a one-page book
    if book_osis:
        if book_osis in ONE_PAGE_BOOKS:
            print(f"Processing single book: {book_osis}")
            book_info = ONE_PAGE_BOOKS[book_osis]
            url = BASE_URL + book_info["url"]

            # Scrape the chapter
            book_name, chapter_number, verses = scrape_chapter(url)

            if not verses:
                print(f"  Failed to extract verses for {book_osis}")
                return bible_data

            # Print book and chapter information
            print(f"  Scraping {book_info['title']} (OSIS: {book_osis})")
            print(f"  Found {len(verses)} verses")

            # Add the book if it doesn't exist
            if book_osis not in bible_data:
                bible_data[book_osis] = {
                    "title": book_info["title"],
                    "chapters": {}
                }

            # Add the chapter (use "1" as chapter number if not provided)
            chapter_num = chapter_number or "1"
            bible_data[book_osis]["chapters"][chapter_num] = verses

            return bible_data
        else:
            print(f"Book {book_osis} is not a one-page book. Will search for it in the index.")

    # First, get the index page
    index_html = get_html(BASE_URL + "_INDEX.HTM")
    if not index_html:
        print("Failed to fetch the index page")
        return bible_data

    soup = BeautifulSoup(index_html, 'html.parser')

    # Find all chapter links - they start with "__P" and end with ".HTM"
    chapter_links = soup.find_all('a', href=re.compile(r'__P.*\.HTM'))

    # Track books we've already processed to avoid duplicates
    processed_chapters = set()

    # Keep track of how many chapters we've processed
    chapter_count = 0

    # Process each link
    total_links = len(chapter_links)
    for i, link in enumerate(chapter_links):
        chapter_url = link['href']

        # Skip if this link isn't a chapter link
        if not re.match(r'__P.*\.HTM', chapter_url):
            continue

        # Skip if we've already processed this chapter
        if chapter_url in processed_chapters:
            continue

        processed_chapters.add(chapter_url)

        # Print progress
        print(f"Processing {i+1}/{total_links}: {chapter_url}")

        # Scrape the chapter
        book_name, chapter_number, verses = scrape_chapter(BASE_URL + chapter_url)

        if not book_name or not chapter_number or not verses:
            print(f"  Skipping {chapter_url} - could not extract data")
            continue

        # Map Spanish book name to standardized OSIS abbreviation
        if book_name in BOOK_MAPPING:
            osis_abbr = BOOK_MAPPING[book_name]
        else:
            print(f"  Unknown book name: {book_name}")
            continue

        # If a specific book is requested, skip all other books
        if book_osis and osis_abbr != book_osis:
            continue

        # Skip if this book is already in the existing data
        if existing_data and osis_abbr in existing_data:
            print(f"  Skipping {osis_abbr} - already in existing data")
            continue

        # Print book and chapter information
        print(f"  Scraping {book_name} (OSIS: {osis_abbr}) - Chapter {chapter_number}")
        print(f"  Found {len(verses)} verses")

        # Add the book if it doesn't exist
        if osis_abbr not in bible_data:
            bible_data[osis_abbr] = {
                "title": book_name,
                "chapters": {}
            }

        # Add the chapter
        bible_data[osis_abbr]["chapters"][chapter_number] = verses

        # Increment chapter count
        chapter_count += 1

        # Check if we've reached the limit
        if limit and chapter_count >= limit:
            print(f"Reached limit of {limit} chapters. Stopping.")
            break

        # Be nice to the server
        time.sleep(0.5)

    # Handle missing books
    print("Processing missing books...")
    for osis_abbr, book_info in ONE_PAGE_BOOKS.items():
        # If a specific book is requested, skip all other books
        if book_osis and osis_abbr != book_osis:
            continue

        # Skip if this book is already in the existing data
        if existing_data and osis_abbr in existing_data:
            print(f"  Skipping {osis_abbr} - already in existing data")
            continue

        print(f"Processing missing book: {osis_abbr}")
        url = BASE_URL + book_info["url"]

        # Scrape the chapter
        book_name, chapter_number, verses = scrape_chapter(url)

        if not verses:
            print(f"  Failed to extract verses for {osis_abbr}")
            continue

        # Print book and chapter information
        print(f"  Scraping {book_info['title']} (OSIS: {osis_abbr})")
        print(f"  Found {len(verses)} verses")

        # Add the book if it doesn't exist
        if osis_abbr not in bible_data:
            bible_data[osis_abbr] = {
                "title": book_info["title"],
                "chapters": {}
            }

        # Add the chapter (use "1" as chapter number if not provided)
        chapter_num = chapter_number or "1"
        bible_data[osis_abbr]["chapters"][chapter_num] = verses

        # Be nice to the server
        time.sleep(0.5)

    return bible_data

def main():
    """Main function to execute the scraper and save the result."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Scrape the Spanish Bible from the Vatican website.')
    parser.add_argument('--limit', type=int, help='Maximum number of chapters to scrape')
    parser.add_argument('--output', type=str, default='data/bible_es.json', help='Output file path (default: data/bible_es.json)')
    parser.add_argument('--force', action='store_true', help='Force re-scraping of all books')
    parser.add_argument('--book', type=str, help='OSIS code of a single book to scrape (e.g., "Jude")')
    args = parser.parse_args()

    output_file = args.output

    # Ensure the output file is in the data directory
    if not output_file.startswith('data/'):
        output_file = f"data/{output_file}"
        print(f"Output will be saved to {output_file}")

    # Load existing data if available and not forcing re-scrape
    existing_data = None
    if not args.force and os.path.exists(output_file):
        print(f"Loading existing data from {output_file}")
        existing_data = load_existing_bible_data(output_file)
        print(f"Loaded {len(existing_data)} books from existing data")

    print("Starting to scrape the Spanish Bible...")
    bible_data = scrape_bible(limit=args.limit, existing_data=existing_data, book_osis=args.book)

    if bible_data:
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(bible_data, f, ensure_ascii=False, indent=2)

        print(f"Bible data saved to {output_file}")
        print(f"Total books: {len(bible_data)}")

        # Count the total number of chapters and verses
        total_chapters = 0
        total_verses = 0
        for book in bible_data.values():
            total_chapters += len(book["chapters"])
            for chapter in book["chapters"].values():
                total_verses += len(chapter)

        print(f"Total chapters: {total_chapters}")
        print(f"Total verses: {total_verses}")
    else:
        print("Failed to scrape Bible data")

if __name__ == "__main__":
    main()

# usage example: python scripts/scrape_vatican_es.py --book Jude --output jude_only.json --force
# outputs Jude only as data/jude_only.json. also forces re-scraping.

# we're missing about half of the verses.
# the script needs to me modified to handle the following format,
# where the entire verse is split into multiple <p> tags:

# <p class="MsoNormal" align="left" style="margin-left:0cm;text-align:left;
# text-indent:0cm">1
# 	<i>Del maestro de coro. </i>
# 	<i>Para flautas. Salmo de David.</i>
# </p>
# <p class="MsoNormal" align="left" style="margin-left:0cm;text-align:left;
# text-indent:0cm">2 Señor, escucha mis palabras, </p>
# <p class="MsoNormal" align="left" style="margin-left:0cm;text-align:left;
# text-indent:0cm">atiende a mis gemidos; </p>
# <p class="MsoNormal" align="left" style="margin-left:0cm;text-align:left;
# text-indent:0cm">3 oye mi clamor, mi Rey y mi Dios, </p>
# <p class="MsoNormal" align="left" style="margin-left:0cm;text-align:left;
# text-indent:0cm">porque te estoy suplicando. </p>
