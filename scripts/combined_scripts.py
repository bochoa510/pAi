# check if dtc list is already made, if not fetch and save to json
# use json list to follow link to each code and extract data from that page
#   - title CODE
#   - sections MEANING, SYMPTOMS, CAUSES, FIXES, RELATED DTCS
#   - link to page
# save data to json file
import requests
from bs4 import BeautifulSoup
import json
import os

OUTPUT_DIR = '../data'
def dtc_list():

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
    

    json_path = os.path.join(OUTPUT_DIR, f"{'dtc_list'}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Saved JSON to {json_path}")

    print("Done! JSON file created with DTC codes and descriptions.")
    return json_path

def main():
    if not os.path.isfile("../data/dtc_list.json"): # find dtc list or create it
        dtc_list_path = dtc_list() 
        print(dtc_list_path)
    else :
        dtc_list_path = "../data/dtc_list.json"
        
    print('json laoded')

    #iterate through each item in list, extract code, meaning


    
if __name__ == '__main__':
    main()