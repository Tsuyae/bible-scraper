import os
import requests
import json

# Mapping of numeric keys to OSIS codes and English names
# The numbering is based on the getBible's API

number_to_osis = {
    "1": {"osis": "Gen", "english_name": "Genesis"},
    "2": {"osis": "Exod", "english_name": "Exodus"},
    "3": {"osis": "Lev", "english_name": "Leviticus"},
    "4": {"osis": "Num", "english_name": "Numbers"},
    "5": {"osis": "Deut", "english_name": "Deuteronomy"},
    "6": {"osis": "Josh", "english_name": "Joshua"},
    "7": {"osis": "Judg", "english_name": "Judges"},
    "8": {"osis": "Ruth", "english_name": "Ruth"},
    "9": {"osis": "1Sam", "english_name": "1 Samuel"},
    "10": {"osis": "2Sam", "english_name": "2 Samuel"},
    "11": {"osis": "1Kgs", "english_name": "1 Kings"},
    "12": {"osis": "2Kgs", "english_name": "2 Kings"},
    "13": {"osis": "1Chr", "english_name": "1 Chronicles"},
    "14": {"osis": "2Chr", "english_name": "2 Chronicles"},
    "15": {"osis": "Ezra", "english_name": "Ezra"},
    "16": {"osis": "Neh", "english_name": "Nehemiah"},
    "17": {"osis": "Esth", "english_name": "Esther"},
    "18": {"osis": "Job", "english_name": "Job"},
    "19": {"osis": "Ps", "english_name": "Psalms"},
    "20": {"osis": "Prov", "english_name": "Proverbs"},
    "21": {"osis": "Eccl", "english_name": "Ecclesiastes"},
    "22": {"osis": "Song", "english_name": "Song of Solomon"},
    "23": {"osis": "Isa", "english_name": "Isaiah"},
    "24": {"osis": "Jer", "english_name": "Jeremiah"},
    "25": {"osis": "Lam", "english_name": "Lamentations"},
    "26": {"osis": "Ezek", "english_name": "Ezekiel"},
    "27": {"osis": "Dan", "english_name": "Daniel"},
    "28": {"osis": "Hos", "english_name": "Hosea"},
    "29": {"osis": "Joel", "english_name": "Joel"},
    "30": {"osis": "Amos", "english_name": "Amos"},
    "31": {"osis": "Obad", "english_name": "Obadiah"},
    "32": {"osis": "Jonah", "english_name": "Jonah"},
    "33": {"osis": "Mic", "english_name": "Micah"},
    "34": {"osis": "Nah", "english_name": "Nahum"},
    "35": {"osis": "Hab", "english_name": "Habakkuk"},
    "36": {"osis": "Zeph", "english_name": "Zephaniah"},
    "37": {"osis": "Hag", "english_name": "Haggai"},
    "38": {"osis": "Zech", "english_name": "Zechariah"},
    "39": {"osis": "Mal", "english_name": "Malachi"},
    "40": {"osis": "Matt", "english_name": "Matthew"},
    "41": {"osis": "Mark", "english_name": "Mark"},
    "42": {"osis": "Luke", "english_name": "Luke"},
    "43": {"osis": "John", "english_name": "John"},
    "44": {"osis": "Acts", "english_name": "Acts"},
    "45": {"osis": "Rom", "english_name": "Romans"},
    "46": {"osis": "1Cor", "english_name": "1 Corinthians"},
    "47": {"osis": "2Cor", "english_name": "2 Corinthians"},
    "48": {"osis": "Gal", "english_name": "Galatians"},
    "49": {"osis": "Eph", "english_name": "Ephesians"},
    "50": {"osis": "Phil", "english_name": "Philippians"},
    "51": {"osis": "Col", "english_name": "Colossians"},
    "52": {"osis": "1Thess", "english_name": "1 Thessalonians"},
    "53": {"osis": "2Thess", "english_name": "2 Thessalonians"},
    "54": {"osis": "1Tim", "english_name": "1 Timothy"},
    "55": {"osis": "2Tim", "english_name": "2 Timothy"},
    "56": {"osis": "Titus", "english_name": "Titus"},
    "57": {"osis": "Phlm", "english_name": "Philemon"},
    "58": {"osis": "Heb", "english_name": "Hebrews"},
    "59": {"osis": "Jas", "english_name": "James"},
    "60": {"osis": "1Pet", "english_name": "1 Peter"},
    "61": {"osis": "2Pet", "english_name": "2 Peter"},
    "62": {"osis": "1John", "english_name": "1 John"},
    "63": {"osis": "2John", "english_name": "2 John"},
    "64": {"osis": "3John", "english_name": "3 John"},
    "65": {"osis": "Jude", "english_name": "Jude"},
    "66": {"osis": "Rev", "english_name": "Revelation"},
    "69": {"osis": "Tob", "english_name": "Tobit"},
    "70": {"osis": "Jdt", "english_name": "Judith"},
    "73": {"osis": "Wis", "english_name": "Wisdom"},
    "74": {"osis": "Sir", "english_name": "Sirach"},
    "75": {"osis": "Bar", "english_name": "Baruch"},
    "80": {"osis": "1Macc", "english_name": "1 Maccabees"},
    "81": {"osis": "2Macc", "english_name": "2 Maccabees"}
}

# Create a reverse mapping from English name to OSIS code
english_to_osis = { mapping["english_name"]: mapping["osis"] for mapping in number_to_osis.values() }

def getBible():
    """
    Fetches the specified Bible version from getBible's API.
    For more information on the API, see: https://getbible.net/docs

    Repository: https://github.com/getbible/v2/tree/master

    The final Bible verses are written to a file named in the format:
    getbible_[ABBREVIATION].json in the data folder.
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

    # Save the raw translations JSON for debugging purposes (optional)
    script_dir = os.path.dirname(os.path.realpath(__file__))
    translations_file = os.path.join(script_dir, "..", "data", "getbible_translations.json")
    try:
        os.makedirs(os.path.dirname(translations_file), exist_ok=True)
        with open(translations_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Translation data saved to {translations_file}")
    except Exception as e:
        print(f"Error saving translations JSON to file: {e}")

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

    # Compute output file path in the data folder using the chosen abbreviation.
    data_dir = os.path.join(script_dir, "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    output_file = os.path.join(data_dir, f"getbible_{chosen_abbr}.json")

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
    for num_key, book_info in books_data.items():
        book_name = book_info.get("name", "Unknown Book")
        book_url = book_info.get("url")
        print(f"\nFetching content for {book_name}...")
        try:
            book_response = requests.get(book_url)
            book_response.raise_for_status()
            book_content = book_response.json()

            # Use the outer numeric key to look up the OSIS code from number_to_osis
            osis_entry = number_to_osis.get(num_key)
            if osis_entry:
                osis_key = osis_entry["osis"]
            else:
                osis_key = book_name

            # Use the API response's book name as the title
            bible_verses[osis_key] = {"title": book_name, "chapters": {}}

            # Process chapters...
            chapters = book_content.get("chapters", [])
            for chapter in chapters:
                # Assume each chapter object has a "chapter" key for its number.
                chapter_num = str(chapter.get("chapter", "unknown"))
                bible_verses[osis_key]["chapters"][chapter_num] = {}
                # Each chapter object contains a list of verses.
                verses = chapter.get("verses", [])
                for verse in verses:
                    # Assume each verse object has a "verse" key for its number.
                    verse_num = str(verse.get("verse", "unknown"))
                    # Remove trailing spaces from the verse text.
                    verse_text = verse.get("text", "").strip()
                    bible_verses[osis_key]["chapters"][chapter_num][verse_num] = verse_text

            # Print the book name from the response as confirmation.
            print(f"Processed book: {book_content.get('name', 'No name provided')}")
        except requests.RequestException as e:
            print(f"Error fetching content for {book_name}: {e}")

    # Write the complete Bible verses data to the output JSON file.
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(bible_verses, f, indent=4, ensure_ascii=False)
        print(f"\nBible verses data saved to {output_file}")
    except Exception as e:
        print(f"Error saving bible verses JSON: {e}")

if __name__ == "__main__":
    getBible()
