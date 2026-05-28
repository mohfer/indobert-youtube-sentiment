import csv
import math
import os


INPUT_DIR = "cleaned"
OUTPUT_DIR = "splits"


def split_cleaned_data(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR, chunk_size=None):
	"""
	Split cleaned CSV files into multiple parts, each containing up to `chunk_size` rows.
	Default chunk_size is taken from the environment variable `SPLIT_CHUNK_SIZE` or 100.
	"""

	os.makedirs(output_dir, exist_ok=True)

	# default chunk size (rows per split file)
	if chunk_size is None:
		try:
			chunk_size = int(os.getenv("SPLIT_CHUNK_SIZE", "100"))
		except Exception:
			chunk_size = 100

	files_written = 0

	for filename in os.listdir(input_dir):
		if not filename.endswith(".csv"):
			continue

		input_path = os.path.join(input_dir, filename)
		video_id = filename.replace("_comments.csv", "")
		video_dir = os.path.join(output_dir, video_id)
		os.makedirs(video_dir, exist_ok=True)

		with open(input_path, "r", encoding="utf-8", newline="") as f:
			reader = csv.DictReader(f)
			rows = list(reader)

		if not rows:
			continue

		num_chunks = math.ceil(len(rows) / chunk_size)
		parts_created = 0

		for index in range(num_chunks):
			start = index * chunk_size
			chunk = rows[start:start + chunk_size]

			if not chunk:
				continue

			output_path = os.path.join(video_dir, f"part{index + 1}.csv")

			with open(output_path, "w", encoding="utf-8", newline="") as f:
				writer = csv.writer(f, quoting=csv.QUOTE_ALL)
				writer.writerow(["content"])
				for row in chunk:
					writer.writerow([row["content"]])

			parts_created += 1
			files_written += 1

		print(f"split: created {parts_created} part(s) for {video_id}")

	print(f"splitting complete: wrote {files_written} split file(s) into '{output_dir}'")
     

if __name__ == "__main__":
	split_cleaned_data()
