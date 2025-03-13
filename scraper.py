import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import re
from collections import defaultdict

# URL to scrape

# URL:
URL = "https://www.biblegateway.com/passage/?search=2%20Maccabees%201&version=NRSVCE"


# General structure of URL to Scrape
# bibleUrl = "https://www.biblegateway.com/passage/?search=[BOOK]%20[NUMBER]&version=NRSVCE"
# with open("bible-idex.json", "r") as file:
#     bible_index_data = json.load(file)

# Fetch the webpage
response = requests.get(URL)
if response.status_code != 200:
    print(f"Error: {response.status_code}")
    exit()

# Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

# Find the main container
container = soup.find("div", class_="version-NRSVCE result-text-style-normal text-html")

# Dictionary to store merged verse fragments
verses_dict = defaultdict(list)

# Find all spans where class matches "Gen-1-N" (Genesis 1: N)
for verse_span in soup.find_all("span", class_=re.compile(r"2Macc-1-\d+")):
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

# Merge verse fragments
verses = [{"verse": verse, "text": " ".join(texts)} for verse, texts in verses_dict.items()]

# Print results
for v in verses:
    print(f"{v['verse']}: {v['text']}")

# Print results
for v in verses:
    print(f"{v['verse']}: {v['text']}")

# Convert to CSV
df = pd.DataFrame(verses)
df.to_csv("data/bible.csv", index=False)

print("Scraping complete! Data saved to data/bible.csv")
