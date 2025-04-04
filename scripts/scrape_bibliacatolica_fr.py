import os
import requests
from bs4 import BeautifulSoup
import json
import time
from collections import defaultdict

# bibliacatholica allows you to compare the portuguese version with other versions.
# we're interested in the french version, so we'll scrape that.

# URL formatting: https://www.bibliacatolica.com.br/biblia-ave-maria-vs-biblia-de-jerusalem/[BOOK_NAME_PORTUGUESE]/[CHAPTER_NUMBER]/
# e.g. https://www.bibliacatolica.com.br/biblia-ave-maria-vs-biblia-de-jerusalem/genesis/1/ - Gênesis 1

bible_dictionary = {
    "Gen": {"name": "Genèse", "slug": "genesis"},
    "Exod": {"name": "Exode", "slug": "exodo"},
    "Lev": {"name": "Lévitique", "slug": "levitico"},
    "Num": {"name": "Nombres", "slug": "numeros"},
    "Deut": {"name": "Deutéronome", "slug": "deuteronomio"},
    "Josh": {"name": "Josué", "slug": "josue"},
    "Judg": {"name": "Juges", "slug": "juizes"},
    "Ruth": {"name": "Ruth", "slug": "rute"},
    "1Sam": {"name": "I Samuel", "slug": "i-samuel"},
    "2Sam": {"name": "II Samuel", "slug": "ii-samuel"},
    "1Kgs": {"name": "I Rois", "slug": "i-reis"},
    "2Kgs": {"name": "II Rois", "slug": "ii-reis"},
    "1Chr": {"name": "I Chroniques", "slug": "i-cronicas"},
    "2Chr": {"name": "II Chroniques", "slug": "ii-cronicas"},
    "Ezra": {"name": "Esdras", "slug": "esdras"},
    "Neh": {"name": "Néhémie", "slug": "neemias"},
    "Esth": {"name": "Esther", "slug": "ester"},
    "Job": {"name": "Job", "slug": "jo"},
    "Ps": {"name": "Psaumes", "slug": "salmos"},
    "Prov": {"name": "Proverbes", "slug": "proverbios"},
    "Eccl": {"name": "Ecclésiaste", "slug": "eclesiastes"},
    "Song": {"name": "Cantique des Cantiques", "slug": "cantico-dos-canticos"},
    "Isa": {"name": "Isaïe", "slug": "isaias"},
    "Jer": {"name": "Jérémie", "slug": "jeremias"},
    "Lam": {"name": "Lamentations", "slug": "lamentacoes"},
    "Ezek": {"name": "Ézéchiel", "slug": "ezequiel"},
    "Dan": {"name": "Daniel", "slug": "daniel"},
    "Hos": {"name": "Osée", "slug": "oseias"},
    "Joel": {"name": "Joël", "slug": "joel"},
    "Amos": {"name": "Amos", "slug": "amos"},
    "Obad": {"name": "Abdias", "slug": "abdias"},
    "Jonah": {"name": "Jonas", "slug": "jonas"},
    "Mic": {"name": "Michée", "slug": "miqueias"},
    "Nah": {"name": "Nahum", "slug": "naum"},
    "Hab": {"name": "Habacuc", "slug": "habacuc"},
    "Zeph": {"name": "Sophonie", "slug": "sofonias"},
    "Hag": {"name": "Aggée", "slug": "ageu"},
    "Zech": {"name": "Zacharie", "slug": "zacarias"},
    "Mal": {"name": "Malachie", "slug": "malaquias"},
    "Matt": {"name": "Saint Matthieu", "slug": "sao-mateus"},
    "Mark": {"name": "Saint Marc", "slug": "sao-marcos"},
    "Luke": {"name": "Saint Luc", "slug": "sao-lucas"},
    "John": {"name": "Saint Jean", "slug": "sao-joao"},
    "Acts": {"name": "Actes des Apôtres", "slug": "atos-dos-apostolos"},
    "Rom": {"name": "Romains", "slug": "romanos"},
    "1Cor": {"name": "I Corinthiens", "slug": "i-corintios"},
    "2Cor": {"name": "II Corinthiens", "slug": "ii-corintios"},
    "Gal": {"name": "Galates", "slug": "galatas"},
    "Eph": {"name": "Éphésiens", "slug": "efesios"},
    "Phil": {"name": "Philippiens", "slug": "filipenses"},
    "Col": {"name": "Colossiens", "slug": "colossenses"},
    "1Thess": {"name": "I Thessaloniciens", "slug": "i-tessalonicenses"},
    "2Thess": {"name": "II Thessaloniciens", "slug": "ii-tessalonicenses"},
    "1Tim": {"name": "I Timothée", "slug": "i-timoteo"},
    "2Tim": {"name": "II Timothée", "slug": "ii-timoteo"},
    "Titus": {"name": "Tite", "slug": "tito"},
    "Phlm": {"name": "Philémon", "slug": "filemon"},
    "Heb": {"name": "Hébreux", "slug": "hebreus"},
    "Jas": {"name": "Saint Jacques", "slug": "sao-tiago"},
    "1Pet": {"name": "I Saint Pierre", "slug": "i-sao-pedro"},
    "2Pet": {"name": "II Saint Pierre", "slug": "ii-sao-pedro"},
    "1John": {"name": "I Saint Jean", "slug": "i-sao-joao"},
    "2John": {"name": "II Saint Jean", "slug": "ii-sao-joao"},
    "3John": {"name": "III Saint Jean", "slug": "iii-sao-joao"},
    "Jude": {"name": "Saint Jude", "slug": "sao-judas"},
    "Rev": {"name": "Apocalypse", "slug": "apocalipse"},
    "Tob": {"name": "Tobie", "slug": "tobias"},
    "Jdt": {"name": "Judith", "slug": "judite"},
    "Wis": {"name": "Sagesse", "slug": "sabedoria"},
    "Sir": {"name": "Ecclésiastique", "slug": "eclesiastico"},
    "Bar": {"name": "Baruch", "slug": "baruc"},
    "1Macc": {"name": "I Maccabées", "slug": "i-macabeus"},
    "2Macc": {"name": "II Maccabées", "slug": "ii-macabeus"}
}


def scrape_bibliacatolica(bible_dictionary=bible_dictionary, output_file="bible_ave_maria.json"):
    """
    Scrapes the entire Bible from Biblia Católica (Ave Maria version).

    :param bible_dictionary: Dictionary of books and their corresponding names and slugs (Portuguese).
    :param output_file: The filename where the scraped JSON will be saved (default: 'bible_ave_maria.json').
    """
    # Ensure the output directory exists
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_file)

    # Initialize a dictionary to store the scraped data
    bible_data = {}

    # Try to load existing data if the file exists
    if os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                bible_data = json.load(f)
            print("Loaded existing progress from file")
        except json.JSONDecodeError:
            print("Could not load existing progress, starting fresh")

    # Headers for requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/110.0.0.0"
    }

    for osis, book_info in bible_dictionary.items():
        # Skip if book is already scraped
        if osis in bible_data:
            print(f"Skipping {book_info['name']} ({osis}) - already scraped")
            continue

        print(f"Scraping {book_info['name']} ({osis})...")
        bible_data[osis] = {
            "title": book_info["name"],
            "french_title": book_info["name"],
            "chapters": {}
        }

        try:
            # First, get the number of chapters for this book
            book_url = f"https://www.bibliacatolica.com.br/biblia-ave-maria/{book_info['slug']}/1/"
            response = requests.get(book_url, headers=headers)
            response.encoding = "utf-8"

            if response.status_code != 200:
                print(f"Error: {response.status_code} - Skipping {book_info['name']}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            chapter_list = soup.find("ul", class_="listChapter")

            if not chapter_list:
                print(f"No chapter list found for {book_info['name']}")
                continue

            # Get the maximum chapter number from the list
            max_chapter = max(
                int(li.find("a").text)
                for li in chapter_list.find_all("li")
                if li.find("a")
            )

            # Now scrape each chapter
            for chapter_num in range(1, max_chapter + 1):
                print(f"Scraping Chapter {chapter_num}...")
                chapter_url = f"https://www.bibliacatolica.com.br/biblia-ave-maria-vs-biblia-de-jerusalem/{book_info['slug']}/{chapter_num}/"

                response = requests.get(chapter_url, headers=headers)
                response.encoding = "utf-8"

                if response.status_code != 200:
                    print(f"Error: {response.status_code} - Skipping {book_info['name']} {chapter_num}")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                entry_section = soup.find("section", class_="entry")

                if not entry_section:
                    print(f"No content found for {book_info['name']} {chapter_num}")
                    continue

                # Initialize chapter dictionary
                bible_data[osis]["chapters"][str(chapter_num)] = {}

                # Find all verse rows
                verse_rows = entry_section.find_all("div", class_="row clearfix")
                for row in verse_rows:
                    # Get the second column which contains the French text
                    french_column = row.find_all("div", class_="col-sm-6 col-md-6 col-lg-6")[1]
                    if not french_column:
                        continue

                    # Find the verse paragraph in the French column
                    verse_p = french_column.find("p", class_="v2")
                    if not verse_p:
                        continue

                    # Extract verse number and text
                    verse_number = verse_p.find("strong").text.strip().replace(".", "")

                    # Get the text from the span.t element
                    verse_text = verse_p.find("span", class_="t").text.strip()

                    # Clean up the verse text
                    verse_text = verse_text.strip()
                    # Remove asterisk at the end if present
                    if verse_text.endswith("*"):
                        verse_text = verse_text[:-1].strip()

                    # Store verse in the dictionary
                    bible_data[osis]["chapters"][str(chapter_num)][verse_number] = verse_text

                # Sleep briefly to avoid getting blocked
                time.sleep(2)

            # Save progress after each book is completed
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(bible_data, f, indent=4, ensure_ascii=False)
            print(f"Saved progress after completing {book_info['name']}")

        except Exception as e:
            print(f"Error while scraping {book_info['name']}: {str(e)}")
            # Save progress even if there was an error
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(bible_data, f, indent=4, ensure_ascii=False)
            print(f"Saved progress after error in {book_info['name']}")
            continue

    print(f"Scraping complete! All verses saved to {output_path}")


if __name__ == "__main__":
    scrape_bibliacatolica(output_file="bible_french.json")
