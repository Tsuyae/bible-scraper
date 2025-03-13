import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
import time
from collections import defaultdict
from urllib.parse import quote_plus


# General structure of URL to Scrape
# bibleUrl = "https://www.biblegateway.com/passage/?search=[BOOK]%20[NUMBER]&version=NRSVCE"
with open("bible-index.json", "r") as file:
    bible_index_data = json.load(file)

# Extract "display", which is the name of the book of the Bible
# and "osis", which is it's respective abbreviation, into a list
books = [(book["display"], book["osis"], book["num_chapters"]) for book in bible_index_data["data"][0]]

# Store all verses in a nested dictionary
bible_data = defaultdict(lambda: defaultdict(dict))

# Loop through each book
for display_name, osis, num_chapters in books:
    print(f"Scraping {display_name} ({osis})...")

    # Encode `display_name` to be URL-safe
    display_query_string = quote_plus(display_name)

    # Loop through each chapter
    for chapter_number in range(1, num_chapters + 1):
        print(f"Scraping Chapter {chapter_number}...")

        # Construct URL
        URL = f"https://www.biblegateway.com/passage/?search={display_query_string}%20{chapter_number}&version=NRSVCE"

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

        # Find the main container
        container = soup.find("div", class_="version-NRSVCE result-text-style-normal text-html")

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

        # Merge verse fragments and store them in the structured dictionary
        for verse, texts in verses_dict.items():
            bible_data[display_name][str(chapter_number)][str(verse)] = " ".join(texts)

        # Sleep briefly to avoid getting blocked
        time.sleep(2)

# Save all verses to a JSON file with UTF-8 encoding
with open("bible_scraped.json", "w", encoding="utf-8") as f:
    json.dump(bible_data, f, indent=4, ensure_ascii=False)

print("Scraping complete! All verses saved to bible_scraped.json")
