import requests
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path

OUTPUT_DIR = Path("../data")
DTC_LIST_FILE = OUTPUT_DIR / "dtc_list.json"

def dtc_list():
    url = "https://www.obd-codes.com/p00-codes"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    ul = soup.select_one('div.container > div.main > p > p > ul')

    if not ul:
        print("Could not find the <ul> element.")
        exit(1)

    data = {}

    for li in ul.find_all('li'):
        full_text = li.text.strip()
        code = full_text[:5].upper()  # Always the first 5 characters
        description = full_text[5:].strip(' -–—:\t')
        data[code] = description

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with DTC_LIST_FILE.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved DTC list to: {DTC_LIST_FILE}")
    return DTC_LIST_FILE


def get_section(soup, label):
    header = soup.find(lambda tag: tag.name in ['h2', 'h3'] and label.lower() in tag.get_text(strip=True).lower())
    if not header:
        return []
    items = []
    for sib in header.find_next_siblings():
        if sib.name in ['h2', 'h3']:
            break
        if sib.name == 'ul':
            items.extend([li.get_text(strip=True) for li in sib.find_all('li')])
        elif sib.name == 'p':
            text = sib.get_text(strip=True)
            if text:
                items.append(text)
    return items


def fetch_dtc_details(code):
    url = f"https://www.obd-codes.com/{code.lower()}"
    print(f"Fetching: {url}")

    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching {code}: {e}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    return {
        "code": code,
        "meaning": get_section(soup, "What Does That Mean?"),
        "symptoms": get_section(soup, "Symptoms"),
        "causes": get_section(soup, "Causes"),
        "fixes": get_section(soup, "Possible Solutions"),
        "related_dtcs": get_section(soup, "Related DTC Discussions"),
        "url": url
    }



def scrape_and_save_details(dtc_data):
    out_path = OUTPUT_DIR / "dtc_details.jsonl"
    with out_path.open("w", encoding="utf-8") as f:
        for code in dtc_data.keys():
            details = fetch_dtc_details(code)
            if details:
                json.dump(details, f, ensure_ascii=False)
                f.write("\n")
    print(f"✅ Saved full DTC detail list to: {out_path}")


def main():
    if not DTC_LIST_FILE.exists():
        dtc_list_path = dtc_list()
    else:
        dtc_list_path = DTC_LIST_FILE

    with dtc_list_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
        print(f"Loaded {len(data)} DTC codes")

    print(list(data.items())[:5])  # print first 5 items


    scrape_and_save_details(data)


    # You can now iterate through `data` to fetch info per code
    # Example:
    # for code, desc in data.items():
    #     print(f"{code}: {desc}")

if __name__ == '__main__':
    main()
