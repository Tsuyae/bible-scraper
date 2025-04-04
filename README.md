# Bible JSON Scraper/Fetcher

A suite of scripts using multiple sources to retrieve the Bible and output it into the following JSON format:

```json
{
  "Gen": {
    "title": "Genesis", // Localized name
    "chapters": {
      "1": {
        "1": "In the beginning ..."
      }
    }
  },
  "Exod": { ... }
}
```

## Catholic Bible Standardization

This project includes a standardized version of the Catholic Bible with the following characteristics:

- Total Books: 73 (46 Old Testament, 27 New Testament)
- Deuterocanonical Books: 7 (Tobit, Judith, Wisdom, Sirach, Baruch, 1 Maccabees, 2 Maccabees)
- Standardized using the [OSIS User's Manual](https://crosswire.org/osis/OSIS%202.1.1%20User%20Manual%2006March2006.pdf)

### OSIS Code Mapping

The following JSON shows the mapping between OSIS codes and English book names:

```json
{
  "Gen": "Genesis",
  "Exod": "Exodus",
  "Lev": "Leviticus",
  "Num": "Numbers",
  "Deut": "Deuteronomy",
  "Josh": "Joshua",
  "Judg": "Judges",
  "Ruth": "Ruth",
  "1Sam": "1 Samuel",
  "2Sam": "2 Samuel",
  "1Kgs": "1 Kings",
  "2Kgs": "2 Kings",
  "1Chr": "1 Chronicles",
  "2Chr": "2 Chronicles",
  "Ezra": "Ezra",
  "Neh": "Nehemiah",
  "Tob": "Tobit",
  "Jdt": "Judith",
  "Esth": "Esther",
  "1Macc": "1 Maccabees",
  "2Macc": "2 Maccabees",
  "Job": "Job",
  "Ps": "Psalms",
  "Prov": "Proverbs",
  "Eccl": "Ecclesiastes",
  "Song": "Song of Songs",
  "Wis": "Wisdom",
  "Sir": "Sirach",
  "Isa": "Isaiah",
  "Jer": "Jeremiah",
  "Lam": "Lamentations",
  "Bar": "Baruch",
  "Ezek": "Ezekiel",
  "Dan": "Daniel",
  "Hos": "Hosea",
  "Joel": "Joel",
  "Amos": "Amos",
  "Obad": "Obadiah",
  "Jonah": "Jonah",
  "Mic": "Micah",
  "Nah": "Nahum",
  "Hab": "Habakkuk",
  "Zeph": "Zephaniah",
  "Hag": "Haggai",
  "Zech": "Zechariah",
  "Mal": "Malachi",
  "Matt": "Matthew",
  "Mark": "Mark",
  "Luke": "Luke",
  "John": "John",
  "Acts": "Acts",
  "Rom": "Romans",
  "1Cor": "1 Corinthians",
  "2Cor": "2 Corinthians",
  "Gal": "Galatians",
  "Eph": "Ephesians",
  "Phil": "Philippians",
  "Col": "Colossians",
  "1Thess": "1 Thessalonians",
  "2Thess": "2 Thessalonians",
  "1Tim": "1 Timothy",
  "2Tim": "2 Timothy",
  "Titus": "Titus",
  "Phlm": "Philemon",
  "Heb": "Hebrews",
  "Jas": "James",
  "1Pet": "1 Peter",
  "2Pet": "2 Peter",
  "1John": "1 John",
  "2John": "2 John",
  "3John": "3 John",
  "Jude": "Jude",
  "Rev": "Revelation"
}
```

## Features

# getBible API Fetcher:

This script (located in the scripts folder as getbible.py) fetches Bible translations and their corresponding verses using the getBible.net API. The user is prompted to select a Bible version, and the script then retrieves the full content for each book.
The final output is a JSON file named in the format getbible_[ABBREVIATION].json stored in the data folder, which is gitignored.

# Bible Gateway Scraper:

The repository also contains a scraper that retrieves Bible data from Bible Gateway. To determine the proper bible_version parameter, refer to the Bible version’s reference in the query string of the site’s URL. For example, for RSV:

```
https://www.biblegateway.com/passage/?search=Genesis%201&version=RSV
```

## Setup Instructions

### Clone the Repository (Github CLI)
```sh
gh repo clone Tsuyae/bible-scraper
cd bible-scraper
```

### Set Up a Virtual Environment
```sh
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# For Windows: venv\Scripts\activate
```

### Install Dependencies
```sh
pip install -r requirements.txt
```

### Run your Script of Choice
```sh
python3 scripts/[SCRIPT_NAME].py
```
