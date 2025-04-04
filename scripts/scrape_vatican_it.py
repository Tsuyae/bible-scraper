import requests
from bs4 import BeautifulSoup
import json
import os
from typing import List, Dict, Optional
from urllib.parse import urljoin
import time
import re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Map of Italian titles to OSIS codes
OSIS_CODES = {
    "Genesi": "Gen",
    "Esodo": "Exod",
    "Levitico": "Lev",
    "Numeri": "Num",
    "Deuteronomio": "Deut",
    "Giosuè": "Josh",
    "Giudici": "Judg",
    "Rut": "Ruth",
    "Samuele 1": "1Sam",
    "Samuele 2": "2Sam",
    "Re 1": "1Kgs",
    "Re 2": "2Kgs",
    "Cronache 1": "1Chr",
    "Cronache 2": "2Chr",
    "Esdra": "Ezra",
    "Neemia": "Neh",
    "Tobi": "Tob",
    "Giuditta": "Jdt",
    "Ester": "Esth",
    "Maccabei 1": "1Macc",
    "Maccabei 2": "2Macc",
    "Giobbe": "Job",
    "Salmi": "Ps",
    "Proverbi": "Prov",
    "Qoelet (Ecclesiaste)": "Eccl",
    "Cantico dei Cantici": "Song",
    "Sapienza": "Wis",
    "Siracide": "Sir",
    "Isaia": "Isa",
    "Geremia": "Jer",
    "Lamentazioni": "Lam",
    "Baruc": "Bar",
    "Ezechiele": "Ezek",
    "Daniele": "Dan",
    "Osea": "Hos",
    "Gioele": "Joel",
    "Amos": "Amos",
    "Abdia": "Obad",
    "Giona": "Jonah",
    "Michea": "Mic",
    "Nahum": "Nah",
    "Abacuc": "Hab",
    "Sofonia": "Zeph",
    "Aggeo": "Hag",
    "Zaccaria": "Zech",
    "Malachia": "Mal",
    "Vangelo secondo Matteo": "Matt",
    "Vangelo secondo Marco": "Mark",
    "Vangelo secondo Luca": "Luke",
    "Vangelo secondo Giovanni": "John",
    "Atti degli Apostoli": "Acts",
    "Romani": "Rom",
    "Corinzi 1": "1Cor",
    "Corinzi 2": "2Cor",
    "Gàlati": "Gal",
    "Efesini": "Eph",
    "Filippesi": "Phil",
    "Colossesi": "Col",
    "Tessalonicesi 1": "1Thess",
    "Tessalonicesi 2": "2Thess",
    "Timoteo 1": "1Tim",
    "Timoteo 2": "2Tim",
    "Tito": "Titus",
    "Filemone": "Phlm",
    "Ebrei": "Heb",
    "Giacomo": "Jas",
    "Pietro 1": "1Pet",
    "Pietro 2": "2Pet",
    "Giovanni 1": "1John",
    "Giovanni 2": "2John",
    "Giovanni 3": "3John",
    "Giuda": "Jude",
    "Apocalisse": "Rev"
}

class VaticanBibleScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=5,  # number of retries
            backoff_factor=1,  # wait 1, 2, 4, 8, 16 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],  # status codes to retry on
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Load existing output if it exists
        self.output_file = "data/vatican_it.json"
        self.output = self.load_output()

    def load_output(self) -> Dict:
        if os.path.exists(self.output_file):
            with open(self.output_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_output(self):
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.output, f, ensure_ascii=False, indent=2)

    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        try:
            print(f"  Fetching {url}")
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"  Error fetching {url}: {str(e)}")
            return None

    def extract_books_and_chapters(self) -> Dict[str, Dict]:
        soup = self.get_soup(self.base_url)
        if not soup:
            return {}

        books = {}
        current_book = None
        current_osis = None

        # Find all font tags with size="2" that contain book titles
        for font in soup.find_all('font', size="2"):
            book_title = font.get_text().strip()
            if book_title in OSIS_CODES:
                current_osis = OSIS_CODES[book_title]
                current_book = {
                    'title': book_title,
                    'chapters': {}
                }
                books[current_osis] = current_book

                # Find the next ul element containing chapter links
                next_ul = font.find_next('ul')
                if next_ul:
                    # Find all chapter links
                    for link in next_ul.find_all('a', href=True):
                        chapter_num = link.get_text().strip()
                        if chapter_num.isdigit():
                            current_book['chapters'][chapter_num] = link['href']

                print(f"Found {len(current_book['chapters'])} chapters for {book_title}")

        return books

    def extract_verses(self, soup: BeautifulSoup) -> Dict[str, str]:
        if not soup:
            return {}

        verses = {}

        # Find the main content area
        content = soup.find('body')
        if not content:
            return {}

        # Get all text nodes
        text = content.get_text()

        # Split by verse markers
        verse_parts = re.split(r'\[(\d+)\]', text)

        # Process each verse
        for i in range(1, len(verse_parts), 2):
            verse_num = verse_parts[i]
            verse_text = verse_parts[i + 1].strip()

            # Clean up the verse text
            verse_text = re.sub(r'\s+', ' ', verse_text)  # Normalize whitespace
            verse_text = verse_text.replace('&quot;', '"')
            verse_text = verse_text.replace('&agrave;', 'à')
            verse_text = verse_text.replace('&egrave;', 'è')
            verse_text = verse_text.replace('&igrave;', 'ì')
            verse_text = verse_text.replace('&ograve;', 'ò')
            verse_text = verse_text.replace('&ugrave;', 'ù')
            verse_text = verse_text.replace('&eacute;', 'é')

            # Remove any trailing navigation or copyright text
            verse_text = re.sub(r'\s*Precedente.*$', '', verse_text)
            verse_text = re.sub(r'\s*Copyright.*$', '', verse_text)

            verses[verse_num] = verse_text.strip()

        return verses

    def scrape_chapter_content(self, chapter_url: str) -> Dict[str, str]:
        soup = self.get_soup(urljoin(self.base_url, chapter_url))
        verses = self.extract_verses(soup)
        print(f"    Found {len(verses)} verses")
        time.sleep(2)  # Increased delay between requests
        return verses

    def scrape_all(self):
        books = self.extract_books_and_chapters()
        print(f"Found {len(books)} books")
        print()

        for osis, book in books.items():
            print(f"Scraping {book['title']}...")

            # Initialize or get existing book data
            if osis not in self.output:
                self.output[osis] = {
                    'title': book['title'],
                    'chapters': {}
                }

            for chapter_num, chapter_url in book['chapters'].items():
                # Skip if we already have this chapter
                if chapter_num in self.output[osis]['chapters']:
                    print(f"  Chapter {chapter_num} (already scraped)")
                    continue

                print(f"  Chapter {chapter_num}")
                verses = self.scrape_chapter_content(chapter_url)
                if verses:
                    self.output[osis]['chapters'][chapter_num] = verses
                    # Save progress after each chapter
                    self.save_output()

            print()

        # Final save
        self.save_output()

def main():
    base_url = "https://www.vatican.va/archive/ITA0001/_INDEX.HTM"
    scraper = VaticanBibleScraper(base_url)
    scraper.scrape_all()

if __name__ == "__main__":
    main()
