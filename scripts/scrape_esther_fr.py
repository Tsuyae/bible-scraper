# this is a script that will scrape esther from this site
# https://www.stepbible.org/?q=version=FreCrampon@reference=Est.1

# there are 16 chapters, so url format is the following:
# https://www.stepbible.org/?q=version=FreCrampon@reference=Est.[N]
# where [N] is the chapter number.
# we'll visit each chapter page and scrape the contents

# visit each page and scrape each verse

# <span dir="ltr" class="verse ltrDirection">
# 	<a name="Esth.1.1" class="verseLink">
# 		<span class="verseNumber">1</span>  # <--- This is the verse number.
# 	</a>
# 	<a name="Esth.1.1" class="verseLink"></a>
#       C'était au temps d'Assuérus, —&nbsp;de cet Assuérus qui régna, depuis l'Inde jusqu'à l'Ethiopie, sur cent vingt-sept provinces,&nbsp;— # <--- This is the actual verse text we want to scrape and store.
# </span>


# We want to scrape and store it like so in the data folder:

# {
#   "Esth": {
#     "title": "Esther",
#     "chapters": {
#       "1": {
#         "1": "This is chapter 1 verse 1..."
#       }
#     }
#   },
# }

import requests
from bs4 import BeautifulSoup
import json
import os
from typing import Dict, Any
import time

def scrape_esther() -> Dict[str, Any]:
    base_url = "https://www.stepbible.org/?q=version=FreCrampon@reference=Est."
    data = {
        "Esth": {
            "title": "Esther",
            "chapters": {}
        }
    }

    # There are 16 chapters in Esther
    for chapter in range(1, 17):
        url = f"{base_url}{chapter}"
        print(f"Scraping chapter {chapter}...")

        # Add delay to be respectful to the server
        time.sleep(1)

        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch chapter {chapter}")
            continue

        soup = BeautifulSoup(response.text, 'html.parser')
        chapter_data = {}

        # Find all verse elements
        verse_elements = soup.find_all('span', class_='verse ltrDirection')

        for verse_element in verse_elements:
            # Get verse number
            verse_number_span = verse_element.find('span', class_='verseNumber')
            if not verse_number_span:
                continue

            verse_number = verse_number_span.text.strip()

            # Get verse text
            # Remove the verse number and links to get clean text
            for a in verse_element.find_all('a'):
                a.decompose()
            for span in verse_element.find_all('span', class_='verseNumber'):
                span.decompose()

            verse_text = verse_element.get_text(strip=True)
            chapter_data[verse_number] = verse_text

        data["Esth"]["chapters"][str(chapter)] = chapter_data

    return data

def save_data(data: Dict[str, Any]) -> None:
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    # Save the data to a JSON file
    with open('data/esther_fr.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    print("Starting Esther French Bible scraper...")
    data = scrape_esther()
    save_data(data)
    print("Scraping completed successfully!")

if __name__ == "__main__":
    main()
