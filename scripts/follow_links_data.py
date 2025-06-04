import requests
from bs4 import BeautifulSoup
import os
import json

BASE_URL = 'https://www.obd-codes.com'
SUMMARY_URL = f'{BASE_URL}/p00-codes'

OUTPUT_DIR = '../data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_first_link():
    print('Fetching summary page...')
    resp = requests.get(SUMMARY_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    first_link = soup.select_one('div.container > div.main > p > p > ul > li > a')
    print(first_link)
    if not first_link:
        raise ValueError("No DTC links found on summary page.")

    code = first_link.text.strip().lower()
    href = soup.select_one('div.container > div.main > p > p > ul > li > a')['href']
    #full_url = BASE_URL + href
    full_url = BASE_URL + "/p0005"  # For testing, replace with actual href if needed
    return code, full_url

def fetch_and_save_page(url, code):
    resp = requests.get(url)
    resp.raise_for_status()

    safe_code = "".join(c if c.isalnum() or c in "-_." else "_" for c in code)
    html_path = os.path.join(OUTPUT_DIR, f"{safe_code}.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(resp.text)

    print(f"Saved to {html_path}")
    return html_path

def extract_data_from_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    data = {}

    # Extract title
    title_tag = soup.select_one('div.container > div.main > h1')
    if title_tag:
        data['title'] = title_tag.get_text(strip=True)

    # Extract all h2 sections and their content
    for h2 in soup.select('div.container > div.main > h2'):
        section_title = h2.get_text(strip=True)
        content_blocks = []
        for sib in h2.find_next_siblings():
            if sib.name == 'h2':
                break
            if sib.name in ['p', 'ul', 'ol']:
                content_blocks.append(sib.get_text(strip=True))
        if content_blocks:
            data[section_title] = content_blocks

    return data

def save_json(data, code):
    code="".join(c if c.isalnum() or c in "-_." else "_" for c in code)
    json_path = os.path.join(OUTPUT_DIR, f"{code}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved JSON to {json_path}")

def main():
    code, url = fetch_first_link()
    html_path = fetch_and_save_page(url, code)
    extracted_data = extract_data_from_html(html_path)
    save_json(extracted_data, code)

if __name__ == '__main__':
    main()