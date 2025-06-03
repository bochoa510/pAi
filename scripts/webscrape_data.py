import requests
from bs4 import BeautifulSoup
import json

url = "https://www.obd-codes.com/p00-codes"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'html.parser')

ul = soup.select_one('div.container > div.main > p > p > ul')

if not ul:
    print("Could not find the target <ul> element.")
    exit(1)

data = {}

for li in ul.find_all('li'):
    a_tag = li.find('a')
    if not a_tag:
        continue
    dtc_code = a_tag.text.strip()
    full_text = li.text.strip()
    description = full_text.replace(dtc_code, '').strip(' -–—:')
    data[dtc_code] = description

with open('p00_dtc_codes.json', 'w') as f:
    json.dump(data, f, indent=4)

print("Done! JSON file created with DTC codes and descriptions.")
