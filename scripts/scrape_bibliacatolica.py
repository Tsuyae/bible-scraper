import os
import requests
from bs4 import BeautifulSoup
import json
import time
from collections import defaultdict

# this script will likely be trashed, too.
# there's no general solution for removing random parenthesis from the inner text of the verses, e.g.:
# Eis que uma Virgem conceberá e dará à luz um filho, que se chamará Emanuel (), que significa: Deus conosco.
# the only solution would be to manually remove them, which is not scalable. we don't have time for that.

# URL formatting: https://www.bibliacatolica.com.br/biblia-ave-maria/[book_name]/[chapter_number]/
# e.g. https://www.bibliacatolica.com.br/biblia-ave-maria/i-cronicas/1/ - I Crônicas 1


bible_dictionary = {
    "Gen": {"name": "Gênesis", "slug": "genesis"},
    "Exod": {"name": "Êxodo", "slug": "exodo"},
    "Lev": {"name": "Levítico", "slug": "levitico"},
    "Num": {"name": "Números", "slug": "numeros"},
    "Deut": {"name": "Deuteronômio", "slug": "deuteronomio"},
    "Josh": {"name": "Josué", "slug": "josue"},
    "Judg": {"name": "Juízes", "slug": "juizes"},
    "Ruth": {"name": "Rute", "slug": "rute"},
    "1Sam": {"name": "I Samuel", "slug": "i-samuel"},
    "2Sam": {"name": "II Samuel", "slug": "ii-samuel"},
    "1Kgs": {"name": "I Reis", "slug": "i-reis"},
    "2Kgs": {"name": "II Reis", "slug": "ii-reis"},
    "1Chr": {"name": "I Crônicas", "slug": "i-cronicas"},
    "2Chr": {"name": "II Crônicas", "slug": "ii-cronicas"},
    "Ezra": {"name": "Esdras", "slug": "esdras"},
    "Neh": {"name": "Neemias", "slug": "neemias"},
    "Esth": {"name": "Ester", "slug": "ester"},
    "Job": {"name": "Jó", "slug": "jo"},
    "Ps": {"name": "Salmos", "slug": "salmos"},
    "Prov": {"name": "Provérbios", "slug": "proverbios"},
    "Eccl": {"name": "Eclesiastes", "slug": "eclesiastes"},
    "Song": {"name": "Cântico dos Cânticos", "slug": "cantico-dos-canticos"},
    "Isa": {"name": "Isaías", "slug": "isaias"},
    "Jer": {"name": "Jeremias", "slug": "jeremias"},
    "Lam": {"name": "Lamentações", "slug": "lamentacoes"},
    "Ezek": {"name": "Ezequiel", "slug": "ezequiel"},
    "Dan": {"name": "Daniel", "slug": "daniel"},
    "Hos": {"name": "Oséias", "slug": "oseias"},
    "Joel": {"name": "Joel", "slug": "joel"},
    "Amos": {"name": "Amós", "slug": "amos"},
    "Obad": {"name": "Abdias", "slug": "abdias"},
    "Jonah": {"name": "Jonas", "slug": "jonas"},
    "Mic": {"name": "Miquéias", "slug": "miqueias"},
    "Nah": {"name": "Naum", "slug": "naum"},
    "Hab": {"name": "Habacuc", "slug": "habacuc"},
    "Zeph": {"name": "Sofonias", "slug": "sofonias"},
    "Hag": {"name": "Ageu", "slug": "ageu"},
    "Zech": {"name": "Zacarias", "slug": "zacarias"},
    "Mal": {"name": "Malaquias", "slug": "malaquias"},
    "Matt": {"name": "São Mateus", "slug": "sao-mateus"},
    "Mark": {"name": "São Marcos", "slug": "sao-marcos"},
    "Luke": {"name": "São Lucas", "slug": "sao-lucas"},
    "John": {"name": "São João", "slug": "sao-joao"},
    "Acts": {"name": "Atos dos Apóstolos", "slug": "atos-dos-apostolos"},
    "Rom": {"name": "Romanos", "slug": "romanos"},
    "1Cor": {"name": "I Coríntios", "slug": "i-corintios"},
    "2Cor": {"name": "II Coríntios", "slug": "ii-corintios"},
    "Gal": {"name": "Gálatas", "slug": "galatas"},
    "Eph": {"name": "Efésios", "slug": "efesios"},
    "Phil": {"name": "Filipenses", "slug": "filipenses"},
    "Col": {"name": "Colossenses", "slug": "colossenses"},
    "1Thess": {"name": "I Tessalonicenses", "slug": "i-tessalonicenses"},
    "2Thess": {"name": "II Tessalonicenses", "slug": "ii-tessalonicenses"},
    "1Tim": {"name": "I Timóteo", "slug": "i-timoteo"},
    "2Tim": {"name": "II Timóteo", "slug": "ii-timoteo"},
    "Titus": {"name": "Tito", "slug": "tito"},
    "Phlm": {"name": "Filêmon", "slug": "filemon"},
    "Heb": {"name": "Hebreus", "slug": "hebreus"},
    "Jas": {"name": "São Tiago", "slug": "sao-tiago"},
    "1Pet": {"name": "I São Pedro", "slug": "i-sao-pedro"},
    "2Pet": {"name": "II São Pedro", "slug": "ii-sao-pedro"},
    "1John": {"name": "I São João", "slug": "i-sao-joao"},
    "2John": {"name": "II São João", "slug": "ii-sao-joao"},
    "3John": {"name": "III São João", "slug": "iii-sao-joao"},
    "Jude": {"name": "São Judas", "slug": "sao-judas"},
    "Rev": {"name": "Apocalipse", "slug": "apocalipse"},
    "Tob": {"name": "Tobias", "slug": "tobias"},
    "Jdt": {"name": "Judite", "slug": "judite"},
    "Wis": {"name": "Sabedoria", "slug": "sabedoria"},
    "Sir": {"name": "Eclesiástico", "slug": "eclesiastico"},
    "Bar": {"name": "Baruc", "slug": "baruc"},
    "1Macc": {"name": "I Macabeus", "slug": "i-macabeus"},
    "2Macc": {"name": "II Macabeus", "slug": "ii-macabeus"}
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
        bible_data[osis] = {"title": book_info["name"], "chapters": {}}

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
                chapter_url = f"https://www.bibliacatolica.com.br/biblia-ave-maria/{book_info['slug']}/{chapter_num}/"

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

                # Find all verse paragraphs
                verse_paragraphs = entry_section.find_all("p")
                for verse_p in verse_paragraphs:
                    # Skip if no strong tag (verse number)
                    if not verse_p.find("strong"):
                        continue

                    # Extract verse number and text
                    verse_number = verse_p.find("strong").text.strip().replace(".", "")

                    # Get the text after the strong tag (verse number)
                    verse_text = ""
                    for content in verse_p.contents:
                        if content.name != "strong":  # Skip the verse number
                            if isinstance(content, str):  # If it's a text node
                                verse_text += content
                            elif content.name is None:  # If it's a NavigableString
                                verse_text += str(content)

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
    scrape_bibliacatolica(output_file="bible_ave_maria.json")
