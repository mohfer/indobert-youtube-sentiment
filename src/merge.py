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
	fieldnames = None

	for input_path in sorted(input_paths):
		with open(input_path, "r", encoding="utf-8", newline="") as f:
			reader = csv.DictReader(f)

			if fieldnames is None:
				fieldnames = reader.fieldnames or []

			for row in reader:
				merged_rows.append(row)

	if not fieldnames:
		print("no valid csv headers found")
		return

	output_path = os.path.join(input_dir, output_file)

	with open(output_path, "w", encoding="utf-8", newline="") as f:
		writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
		writer.writeheader()
		writer.writerows(merged_rows)

	print(f"merged {len(input_paths)} files into {output_path}")


if __name__ == "__main__":
	merge_csv_files()
