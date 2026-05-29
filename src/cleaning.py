import os
import json
import re
import csv
from splitting import split_cleaned_data

INPUT_DIR = "scraped"
OUTPUT_DIR = "cleaned"

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

def clean_text(text):

    text = text.lower()

    text = re.sub(
        r'http\S+|www\S+',
        '',
        text
    )

    text = re.sub(
        r'@\w+',
        '',
        text
    )

    text = re.sub(
        r'#(\w+)',
        r'\1',
        text
    )

    text = re.sub(
        r'\s+',
        ' ',
        text
    )

    text = re.sub(
        r'(.)\1{2,}',
        r'\1\1',
        text
    )

    text = re.sub(
        r'([!?])\1{2,}',
        r'\1\1',
        text
    )

    text = text.strip()

    return text

for filename in os.listdir(INPUT_DIR):

    if not filename.endswith(".json"):
        continue

    input_path = os.path.join(
        INPUT_DIR,
        filename
    )

    output_path = os.path.join(
        OUTPUT_DIR,
        filename.replace(".json", ".csv")
    )

    with open(
        input_path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    cleaned_data = []

    for item in data:

        content = item.get(
            "content",
            ""
        )

        cleaned = clean_text(content)

        if not cleaned:
            continue

        cleaned_data.append({
            "content": cleaned
        })

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline=""
    ) as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["content"])
        for row in cleaned_data:
            writer.writerow([row["content"]])

    print(
        f"cleaned: {filename}"
    )

split_cleaned_data()