import requests
import json

def getBible(output_file="getBible.json"):
    """
    Fetches the specified Bible version from getBible's API.
    For more information on the API, see: https://getbible.net/docs
    Repository: https://github.com/getbible/v2/tree/master

    :param output_file: The filename where the scraped JSON will be saved (default: 'getBible.json').
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

    return chosen_abbr, chosen_name

if __name__ == "__main__":
    getBible()
