import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from bs4 import BeautifulSoup
import requests
import json

BASE_URL = "https://www.obd-codes.com/"
LIST_URL = f"{BASE_URL}p00-codes"

class ExtractDTCList(beam.DoFn):
    def process(self, element):
        response = requests.get(LIST_URL, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, 'html.parser')
        ul = soup.select_one('div.container > div.main > p > p > ul')
        if not ul:
            return
        for li in ul.find_all('li'):
            text = li.text.strip()
            code = text[:5].upper()
            description = text[5:].strip(' -–—:\t')
            yield (code, description)

class FetchDTCDetails(beam.DoFn):
    def process(self, dtc_tuple):
        code, description = dtc_tuple
        url = f"{BASE_URL}{code.lower()}"
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            sections = ['Meaning', 'Symptoms', 'Causes', 'Diagnostic Steps', 'Related codes']
            content = {}
            for header in soup.find_all(['h2', 'h3']):
                title = header.get_text(strip=True)
                for section in sections:
                    if section.lower() in title.lower():
                        next_p = header.find_next_sibling('p')
                        if next_p:
                            content[section.lower()] = next_p.get_text(strip=True)

            yield json.dumps({
                "code": code,
                "description": description,
                "url": url,
                **content
            }, ensure_ascii=False)

        except Exception as e:
            yield beam.pvalue.TaggedOutput('errors', f"{code}: {str(e)}")

def run():
    options = PipelineOptions()
    with beam.Pipeline(options=options) as p:
        results = (
            p
            | "Start" >> beam.Create([None])
            | "ExtractDTCList" >> beam.ParDo(ExtractDTCList())
            | "FetchDetails" >> beam.ParDo(FetchDTCDetails()).with_outputs('errors', main='data')
        )

        results.data | "WriteOutput" >> beam.io.WriteToText(
            "../data/dtc_output", file_name_suffix=".jsonl", shard_name_template="")

        results.errors | "WriteErrors" >> beam.io.WriteToText(
            "../data/dtc_errors", file_name_suffix=".log", shard_name_template="")

if __name__ == '__main__':
    run()
