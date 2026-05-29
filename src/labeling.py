import os
import glob
import re
import time
from pathlib import Path
from dotenv import load_dotenv
try:
    from openai import OpenAI
except ImportError:
    print("OpenAI module not installed. Run: uv add openai")
    exit(1)
    
load_dotenv()

# Endpoint and OpenAI compatible API configuration
CLIENT_BASE_URL = os.getenv("CLIENT_BASE_URL", "https://api.openai.com/v1")
CLIENT_API_KEY = os.getenv("CLIENT_API_KEY", "your-api-key-here")
MODEL = os.getenv("MODEL", "gpt-5.5")

try:
    client = OpenAI(
        base_url=CLIENT_BASE_URL,
        api_key=CLIENT_API_KEY,
    )
except Exception as e:
    print(f"Failed to initialize OpenAI client: {e}")
    exit(1)

SYSTEM_PROMPT = """Tolong beri label, positif, negatif, netral pada data yang diberikan. 

KEMBALIKAN OUTPUT HANYA BERUPA TEKS CSV MURNI. 
Format output HARUS persis seperti contoh ini:
content,label
"starbucks keliling",netral
"koneksinya cepat sekali",positif
"kualitasnya ampas bener",negatif

PENTING:
- Buat hasilnya seakurat mungkin karena ini untuk data latih fine tuning model indobert-base analisis sentiment komentar youtube.
- BACA MANUAL SATU PERSATU, tentukan label berdasarkan makna, jangan hanya rule based.
- Jangan gunakan block markdown (seperti ```csv). 
- DILARANG menyertakan kata-kata pengantar atau penutup. Output murni harus berupa teks baris-baris CSV.
"""

def get_next_output_filename(data_dir="data"):
    """
    Search for files in the data directory with the format dataX.csv, 
    and return the filename with the next number X (e.g., data11.csv if data10.csv exists).
    """
    os.makedirs(data_dir, exist_ok=True)
    files = glob.glob(os.path.join(data_dir, "data*.csv"))
    max_num = 0
    for f in files:
        m = re.search(r'data(\d+)\.csv', os.path.basename(f))
        if m:
            max_num = max(max_num, int(m.group(1)))
    return os.path.join(data_dir, f"data{max_num + 1}.csv")

def process_chunk(csv_path):
    print(f"\n[AI Labeling] Processing file: {csv_path}")
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Limit request if file is empty or contains only a header
    if not content.strip() or len(content.strip().split('\n')) <= 1:
        print(" -> File seems to be empty. Skipping.")
        return
    
    user_prompt = f"Berikut adalah data komentarnya:\n\n{content}"
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1 # Low temperature for more accurate and deterministic outputs
        )
        
        reply = response.choices[0].message.content.strip()
        
        # Remove thinking blocks if the model is a reasoning/thinking model
        reply = re.sub(r'<thinking>.*?</thinking>', '', reply, flags=re.DOTALL).strip()
        
        # Additional cleanup in case it outputs thinking inside other tags or as thought
        reply = re.sub(r'<thought>.*?</thought>', '', reply, flags=re.DOTALL).strip()
        
        # Clean formatting if the model still wraps output in markdown blocks
        if reply.startswith("```csv"):
            reply = reply[6:]
        elif reply.startswith("```"):
            reply = reply[3:]
        if reply.endswith("```"):
            reply = reply[:-3]
            
        reply = reply.strip()
        
        output_file = get_next_output_filename()
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(reply)
            
        print(f" -> ✅ Successfully labeled and saved as: {output_file}")
        
        # Rename the processed split file to avoid reprocessing in the next run
        processed_path = csv_path + ".done"
        os.rename(csv_path, processed_path)
            
    except Exception as e:
        print(f" -> ❌ An error occurred during the API request: {e}")

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def main():
    splits_dir = "splits"
    if not os.path.exists(splits_dir):
        print(f"Directory '{splits_dir}' not found. Please run the split pipeline first.")
        return
        
    chunk_files = []
    # Find all CSV files in the splits/ directory that haven't been marked as .done
    for root, dirs, files in os.walk(splits_dir):
        for file in files:
            if file.endswith(".csv"):
                chunk_files.append(os.path.join(root, file))
                
    if not chunk_files:
        print("No chunk CSV files found in splits/ directory that need labeling (all may have been labeled).")
        return
        
    # Sort naturally so processing follows part1, part2, ... part10, instead of random order
    chunk_files.sort(key=natural_sort_key)
        
    print(f"Found {len(chunk_files)} unlabeled CSV chunk files.")
    print(f"Starting sequential processing for {len(chunk_files)} chunks (one API prompt per file)...")
    
    for i, chunk_to_process in enumerate(chunk_files, 1):
        print(f"\n--- Processing part {i} of {len(chunk_files)} ---")
        process_chunk(chunk_to_process)
        
        if i < len(chunk_files):
            print(" -> Waiting 2 seconds before requesting the next part...")
            time.sleep(2)
            
    print("\nAll data chunks have been successfully auto-labeled.")

if __name__ == "__main__":
    main()
