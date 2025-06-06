import requests
from bs4 import BeautifulSoup
import os
import json

BASE_URL = 'https://www.obd-codes.com'
SUMMARY_URL = f'{BASE_URL}/p00-codes'  # Change if needed

# Create base output directories
OUTPUT_DIR = '../data'
HTML_DIR = os.path.join(OUTPUT_DIR, 'html')
JSON_DIR = os.path.join(OUTPUT_DIR, 'json')
os.makedirs(HTML_DIR, exist_ok=True)
os.makedirs(JSON_DIR, exist_ok=True)

def fetch_first_link():
    print('Fetching summary page...')
    resp = requests.get(SUMMARY_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    # Find first DTC link
    first_link = soup.select_one('div.container > div.main > p > p > ul')
    if not first_link:
        raise ValueError("No DTC links found on summary page.")

    code = first_link.text.strip().lower()
    code = code[:5]
    print (code)
   # code = first_link.text.rstrip()
    href = soup.select_one('div.container > div.main > p > p > ul > li > a')['href']
    full_url = BASE_URL + href
    return code, full_url

def fetch_and_save_page(url, code):
    resp = requests.get(url)
    resp.raise_for_status()

    # Sanitize filename
  #  safe_code = "".join(c if c.isalnum() or c in "-_." else "_" for c in code)
    
    # Save HTML
    html_path = os.path.join(HTML_DIR, f"{code}.html")

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(resp.text)
    print(f"Saved HTML to {html_path}")

    # Placeholder for saving JSON if needed
    json_path = os.path.join(JSON_DIR, f"{code}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({"code": code, "url": url}, f, indent=2)

def main():
    code, url = fetch_first_link()
    fetch_and_save_page(url, code)

if __name__ == '__main__':
    main()
