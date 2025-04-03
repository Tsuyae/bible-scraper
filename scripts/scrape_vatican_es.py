import requests
from bs4 import BeautifulSoup
import json

# this script will likely be trashed.
# the html structure of the vatican's spanish bible is not very good.
# it requires a scraper... to scrape the scraper. cool and good.

def scrape_vatican_es():
    # Base URL for the Vatican's Spanish Bible
    base_url = "https://www.vatican.va/archive/ESL0506/_INDEX.HTM"

    # Dictionary to store the book chapters and their links
    bible_links = {}

    try:
        # Fetch the index page
        response = requests.get(base_url)
        response.raise_for_status()

        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all book entries (they have font size="3")
        book_entries = soup.find_all('font', size="3")

        for book_entry in book_entries:
            # Get the book name - handle both cases where it's a link or just text
            book_link = book_entry.find('a')
            if book_link:
                # Case 1: Book name is a link
                book_name = book_link.text.strip()
            else:
                # Case 2: Book name is just text in the font tag
                book_name = book_entry.text.strip()

            # Find the chapter list (it's in a ul with type="square" right after the book entry)
            chapter_list = book_entry.find_next('ul', type="square")
            if not chapter_list:
                continue

            # Dictionary to store chapters for this book
            chapters = {}

            # Find all chapter links (they have font size="2")
            chapter_entries = chapter_list.find_all('font', size="2")
            for chapter_entry in chapter_entries:
                chapter_links = chapter_entry.find_all('a')
                for link in chapter_links:
                    chapter_num = link.text.strip().rstrip('.')
                    chapter_url = link['href']
                    chapters[chapter_num] = chapter_url

            # Add the book and its chapters to the main dictionary
            bible_links[book_name] = chapters

        # Save the dictionary to a JSON file
        with open('vatican_es_bible_links.json', 'w', encoding='utf-8') as f:
            json.dump(bible_links, f, ensure_ascii=False, indent=2)

        print(f"Successfully scraped {len(bible_links)} books and saved to vatican_es_bible_links.json")
        return bible_links

    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    scrape_vatican_es()






# sometimes the title of a book will not be a link (<a/>), but a font (<font/>):

# <font size="3">SEGUNDO LIBRO DE SAMUEL</font>

# <font size="3"><a href="__P6O.HTM">PRIMER LIBRO DE SAMUEL</a></font>

# so we need to handle both cases.

# we can do this by checking if the book_link is a link (<a/>) or a font (<font/>).


