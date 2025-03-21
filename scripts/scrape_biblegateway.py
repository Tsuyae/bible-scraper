import os
import requests
from bs4 import BeautifulSoup
import json
import re
import time
from collections import defaultdict
from urllib.parse import quote_plus


def scrape_biblegateway(bible_version="NRSVCE", bible_index_file="bible_index.json", output_file="bible_scraped.json"):
    """
    Scrapes the entire Bible from BibleGateway using the specified version.

    :param bible_version: The translation/version to scrape (e.g., 'NRSVCE', 'KJV', 'ESV').
    :param bible_index_file: JSON file containing the list of books, chapters, and OSIS codes.
    :param output_file: The filename where the scraped JSON will be saved (default: 'bible_scraped.json').
    """

    # Ensure the output directory exists
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    os.makedirs(output_dir, exist_ok=True)  # Create "data/" folder if it doesn't exist
    output_path = os.path.join(output_dir, output_file)  # Full path to output JSON file

    # Load JSON data (list of books and chapters)
    with open(bible_index_file, "r", encoding="utf-8") as file:
        bible_index_data = json.load(file)

    # Extract book names and OSIS codes
    books = [(book["display"], book["osis"], book["num_chapters"]) for book in bible_index_data["data"][0]]

    # Store all verses in a nested dictionary using the desired structure
    bible_data = {}

    for display_name, osis, num_chapters in books:
        print(f"Scraping {display_name} ({osis}) in {bible_version}...")

        # Initialize the dictionary for this book using OSIS as the key and store the title
        bible_data[osis] = {"title": display_name, "chapters": {}}

        # Loop through each chapter
        for chapter_number in range(1, num_chapters + 1):
            print(f"Scraping Chapter {chapter_number}...")

            # Construct URL dynamically
            display_query_string = quote_plus(display_name)
            URL = f"https://www.biblegateway.com/passage/?search={display_query_string}%20{chapter_number}&version={bible_version}"

            # Fetch the webpage
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/110.0.0.0"
            }
            response = requests.get(URL, headers=headers)

            # Force UTF-8 encoding to avoid bad characters
            response.encoding = "utf-8"

            if response.status_code != 200:
                print(f"Error: {response.status_code} - Skipping {display_name} {chapter_number}")
                continue  # Skip to the next chapter

            # Parse the HTML
            soup = BeautifulSoup(response.text, "html.parser")

            # Dictionary to store merged verse fragments
            verses_dict = defaultdict(list)

            # Find all spans where class matches "[OSIS]-[CHAPTER_NUMBER]-N" (e.g., "Gen-1-1")
            for verse_span in soup.find_all("span", class_=re.compile(fr"{osis}-{chapter_number}-\d+")):
                # Ensure the span is NOT inside a heading tag (<h1>, <h2>, <h3>, etc.)
                if verse_span.find_parent(re.compile(r"h\d")):
                    continue  # Skip headings

                # Extract the verse number (last part of class name)
                verse_number = verse_span["class"][1].split("-")[-1]

                # Remove unwanted elements: footnotes and chapter numbers
                for sup in verse_span.find_all("sup"):
                    if not re.match(r"^\d+$", sup.get_text(strip=True)):  # If not numeric
                        sup.insert_before(" ")  # Add space before footnote removal
                        sup.decompose()  # Remove the footnote tag
                for chapternum in verse_span.find_all("span", class_="chapternum"):
                    chapternum.decompose()  # Completely remove chapter numbers

                # Extract cleaned verse text
                verse_text = verse_span.get_text(" ", strip=True)  # Ensures spacing remains intact

                # Remove verse number from text
                verse_text = verse_text.replace(verse_number, "").strip()

                # Store text in dictionary, grouped by verse number
                verses_dict[verse_number].append(verse_text)

            # Ensure the chapter key exists under 'chapters'
            bible_data[osis]["chapters"][str(chapter_number)] = {}

            # Merge verse fragments and store them in the structured dictionary
            for verse, texts in verses_dict.items():
                bible_data[osis]["chapters"][str(chapter_number)][str(verse)] = " ".join(texts)

            # Sleep briefly to avoid getting blocked
            time.sleep(2)

    # Save all verses to a JSON file with UTF-8 encoding
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(bible_data, f, indent=4, ensure_ascii=False)

    print(f"Scraping complete! All verses saved to {output_path}")


scrape_biblegateway(bible_version="NRSVCE", output_file="bible_nrsvce.json")
