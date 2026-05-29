import csv
import os

INPUT_DIR = "data"
OUTPUT_FILE = "sentiment.csv"

def merge_csv_files(input_dir=INPUT_DIR, output_file=OUTPUT_FILE):
    input_paths = []

    for filename in os.listdir(input_dir):
        if not filename.endswith(".csv"):
            continue

        if filename == output_file:
            continue

        input_paths.append(os.path.join(input_dir, filename))

    if not input_paths:
        print("no csv files to merge")
        return

    merged_rows = []
    fieldnames = ['content', 'label']

    for input_path in sorted(input_paths):
        with open(input_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            
            for row in reader:
                if not row:
                    continue
                if len(row) > 2:
                    # AI labeling might output more than 2 columns if it includes commas in the content. We assume the last column is the label and everything before it is content.
                    # This is a simple heuristic and may not be perfect if the content itself contains commas, but it should work for most cases.
                    content = ",".join(row[:-1])
                    label = row[-1]
                elif len(row) == 2:
                    content, label = row[0], row[1]
                else:
                    content, label = row[0], ""
                
                merged_rows.append({'content': content, 'label': label})

    if not merged_rows:
        print("no valid csv data found")
        return

    output_path = os.path.join(input_dir, output_file)

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(merged_rows)

    print(f"merged {len(input_paths)} files into {output_path}")

if __name__ == "__main__":
    merge_csv_files()
