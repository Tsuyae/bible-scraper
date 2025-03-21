import requests
import json

def getBible(output_file="getBible.json"):
    """
    Fetches the specified Bible version from getBible's API.
    For more information on the API, see: https://getbible.net/docs
    Repository: https://github.com/getbible/v2/tree/master

    :param output_file: The filename where the translations JSON will be saved (default: 'getBible.json').
    """
    translations_url = "https://api.getbible.net/v2/translations.json"

    # Fetch translations JSON from the API
    try:
        response = requests.get(translations_url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching translations: {e}")
        return

    data = response.json()

    # Save the raw JSON data to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Translation data saved to {output_file}")
    except Exception as e:
        print(f"Error saving JSON to file: {e}")

    # Extract translations list
    translations = []
    for abbr, info in data.items():
        if isinstance(info, dict) and "translation" in info:
            translations.append((abbr, info.get("translation", "Unknown")))

    if not translations:
        print("No translations found.")
        return

    # Display a menu of available translations
    print("\nSelect a Bible version:")
    for idx, (abbr, name) in enumerate(translations, start=1):
        print(f"{idx}. {abbr} - {name}")

    # Prompt the user to select a translation
    while True:
        try:
            selection = int(input("Enter the number of your chosen Bible version: "))
            if 1 <= selection <= len(translations):
                break
            else:
                print("Invalid selection. Please choose a valid number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    chosen_abbr, chosen_name = translations[selection - 1]
    print(f"\nYou selected: {chosen_name} (abbreviation: {chosen_abbr})")

    # Fetch the books index for the chosen Bible version
    books_url = f"https://api.getbible.net/v2/{chosen_abbr}/books.json"
    try:
        books_response = requests.get(books_url)
        books_response.raise_for_status()
        books_data = books_response.json()
    except requests.RequestException as e:
        print(f"Error fetching books index: {e}")
        return

    # This dictionary will hold the final Bible verses structure.
    bible_verses = {}

    # For each book in the books index, fetch its content and extract verses.
    for key, book_info in books_data.items():
        book_name = book_info.get("name", "Unknown Book")
        book_url = book_info.get("url")
        print(f"\nFetching content for {book_name}...")
        try:
            book_response = requests.get(book_url)
            book_response.raise_for_status()
            book_content = book_response.json()

            # Initialize the dictionary for this book using the book name.
            bible_verses[book_name] = {}

            # chapters is now expected to be a list of chapter objects.
            chapters = book_content.get("chapters", [])
            for chapter in chapters:
                # Assume each chapter object has a "chapter" key for its number.
                chapter_num = str(chapter.get("chapter", "unknown"))
                bible_verses[book_name][chapter_num] = {}
                # Each chapter object contains a list of verses.
                verses = chapter.get("verses", [])
                for verse in verses:
                    # Assume each verse object has a "verse" key for its number.
                    verse_num = str(verse.get("verse", "unknown"))
                    # Remove trailing spaces from the verse text.
                    verse_text = verse.get("text", "").strip()
                    bible_verses[book_name][chapter_num][verse_num] = verse_text

            # Print the book name from the response as confirmation.
            print(f"Processed book: {book_content.get('name', 'No name provided')}")
        except requests.RequestException as e:
            print(f"Error fetching content for {book_name}: {e}")

    # Write the complete Bible verses data to a JSON file.
    output_verses_file = "bible_verses.json"
    try:
        with open(output_verses_file, "w", encoding="utf-8") as f:
            json.dump(bible_verses, f, indent=4, ensure_ascii=False)
        print(f"\nBible verses data saved to {output_verses_file}")
    except Exception as e:
        print(f"Error saving bible verses JSON: {e}")

if __name__ == "__main__":
    getBible()
