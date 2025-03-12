# Bible Gateway Scraper

A simple web scraper using **BeautifulSoup** to extract Bible verses from the **Bible Gateway Website**.

## Features
- To be **decided**.

## Project Structure
```
📁 bible-scraper
│-- 📜 scraper.py        # Main scraping script
│-- 📜 .gitignore        # Ignore unnecessary files
│-- 📜 README.md         # This documentation
│-- 📜 requirements.txt  # Dependencies list
│-- 📁 data/             # Output CSV files (ignored by Git)
```

## Setup Instructions

### Clone the Repository (Github CLI)
```sh
gh repo clone Tsuyae/bible-scraper
cd bible-gateway-scraper
```

### 2️⃣ Set Up a Virtual Environment
```sh
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# For Windows: venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Get API Access Token
1. Sign up for an API key from **Bible Gateway**.
2. Use your credentials to obtain an `access_token`:
   ```sh
   curl -X GET "https://api.biblegateway.com/2/request_access_token?username=your_username&password=your_password"
   ```
3. Store the token in a **`.env`** file:
   ```ini
   ACCESS_TOKEN=your_token_here
   ```

### 5️⃣ Run the Scraper
```sh
python scraper.py
```

## 📝 Example API Request in Python
```python
import requests

url = "https://api.biblegateway.com/2/bible/osis/Gen.1.1/NRSVCE"
params = {"access_token": "your_token_here"}

response = requests.get(url, params=params)
print(response.json())
```

## 🛠️ Troubleshooting
- **Issue:** `ModuleNotFoundError: No module named 'bs4'`
  - **Fix:** Run `pip install beautifulsoup4`
- **Issue:** `Invalid access_token`
  - **Fix:** Ensure your API key is valid and not expired.

