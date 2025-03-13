# Bible Gateway Scraper

A simple web scraper using **BeautifulSoup** to extract Bible verses from the **Bible Gateway Website**. The Bible is then exported as a JSON in the following format:

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

- The Python script in the scripts folder allows the user to scrape any Bible version hosted on Bible Gateway. To find what to pass in as ```bible_version```, refer to the Bible version's reference in the query string in site's URL. E.g., for RSV:

```
https://www.biblegateway.com/passage/?search=Genesis%201&version=RSV
```

## Setup Instructions

### Clone the Repository (Github CLI)
```sh
gh repo clone Tsuyae/bible-scraper
cd bible-gateway-scraper
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

### Run the Scraper
```sh
python main.py
```
