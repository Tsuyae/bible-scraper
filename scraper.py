import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

# URL to scrape

# Test URL:
URL = "https://quotes.toscrape.com/"


# General structure of URL to Scrape
# bibleUrl = "https://www.biblegateway.com/passage/?search=[BOOK]%20[NUMBER]&version=NRSVCE"
# with open("bible-idex.json", "r") as file:
#     bible_index_data = json.load(file)

# Fetch the webpage
response = requests.get(URL)
if response.status_code != 200:
    print(f"Error: {response.status_code}")
    exit()

# Parse the HTML
soup = BeautifulSoup(response.text, "html.parser")

# Extract data
quotes_list = []
for quote in soup.find_all("div", class_="quote"):
    text = quote.find("span", class_="text").get_text(strip=True)
    author = quote.find("small", class_="author").get_text(strip=True)
    quotes_list.append({"Quote": text, "Author": author})

# Convert to CSV
df = pd.DataFrame(quotes_list)
df.to_csv("data/data.csv", index=False)

print("Scraping complete! Data saved to quotes.csv")
