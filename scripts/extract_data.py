# script to extract data from raw data, creating json file for training
import json
import re

# Input file path (replace with your file path)
input_file = ""
output_file = "dtc_codes.json"

# Dictionary to hold parsed DTCs
dtc_dict = {}

# Read the file and parse each line
with open(input_file, "r", encoding="utf-8") as file:
    for line in file:
        match = re.match(r"^(P\d{4})\s+(.*)", line.strip())
        if match:
            code, description = match.groups()
            dtc_dict[code] = description

# Write to JSON
with open(output_file, "w", encoding="utf-8") as json_file:
    json.dump(dtc_dict, json_file, indent=2)

print(f"Parsed {len(dtc_dict)} DTC codes into {output_file}")

