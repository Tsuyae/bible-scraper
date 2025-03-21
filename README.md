
# Bible JSON Scraper/Fetcher

A suite of scripts using multiple sources to retrieve/scrape the bible and output it into the following format:

```json
{
    "Genesis": {
        "1": {
            "1": "In the beginning when God created the heavens and the earth,",
            .
            .
            .
```

## Features

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
python scripts/[SCRIPT_NAME].py
```
