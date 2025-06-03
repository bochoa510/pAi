import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = 'https://www.obd-codes.com'

# Put the URL where the list of codes is
SUMMARY_URL = f'{BASE_URL}/p00-codes'  # Change this to the actual summary page URL

def fetch_summary():
    print('Fetching summary page...')
    resp = requests.get(SUMMARY_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Find the <ul> or container holding the codes — update selector based on real HTML
    ul = soup.select_one('div.container > div.main > p > p > ul')
    
    if not ul:
        raise ValueError("Could not find the list container on summary page.")
    
    links = []
    for a in ul.find_all('a', href=True):
        href = a['href']
        if href.startswith('/p'):
            full_url = BASE_URL + href
            code = href.strip('/').lower()
            links.append({'code': code, 'url': full_url})
    return links

def fetch_details(url):
    print(f'Fetching details for {url}...')
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Extract details from the details page — update selector based on page structure
    # Example: maybe the description is in <div class="content"> or similar
    content_div = soup.select_one('div.content')
    if not content_div:
        return None
    
    description = content_div.get_text(separator='\n').strip()
    return description

def main():
    codes_data = {}
    try:
        links = fetch_summary()
    except Exception as e:
        print(f"Error fetching summary: {e}")
        return
    
    for info in links:
        code = info['code']
        url = info['url']
        try:
            description = fetch_details(url)
            if description:
                codes_data[code] = description
            else:
                print(f"No details found for {code}")
        except Exception as e:
            print(f"Failed to fetch details for {code}: {e}")
        time.sleep(1)  # polite delay between requests
    
    # Save to JSON file
    with open('dtc_details.json', 'w', encoding='utf-8') as f:
        json.dump(codes_data, f, ensure_ascii=False, indent=2)
    
    print("Done! Data saved to dtc_details.json")

if __name__ == '__main__':
    main()
