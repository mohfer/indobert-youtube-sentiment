from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
from bs4 import NavigableString

import os
import time
import json
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

raw_urls = os.getenv("VIDEO_URL", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
video_urls = [u.strip() for u in raw_urls.split(",") if u.strip()]

TARGET_COMMENT = os.getenv("TARGET_COMMENT", 200)
TARGET_COMMENT = int(TARGET_COMMENT)

options = Options()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--user-agent=Mozilla/5.0")

def get_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else "unknown"

def parse_comment(tag):
    result = ""
    for child in tag.descendants:
        if isinstance(child, NavigableString):
            result += str(child)
        elif child.name == "img":
            result += child.get("alt", "")
    return result.strip()

driver = webdriver.Chrome(options=options)
Path("scraped").mkdir(exist_ok=True)

for video_url in video_urls:
    video_id = get_video_id(video_url)
    print(f"\nProcessing video: {video_url} (ID: {video_id})")
    
    driver.get(video_url)
    print("Loading page...")
    time.sleep(5)
    
    driver.execute_script("window.scrollTo(0, 3000);")
    time.sleep(3)
    
    last_count = 0
    no_change = 0
    
    for i in range(30):
        driver.execute_script("window.scrollBy(0, 2000);")
        time.sleep(2)
        
        comments = driver.find_elements(By.CSS_SELECTOR, "#content-text")
        current_count = len(comments)
        
        print(f"scroll {i+1} -> {current_count}")
        
        if current_count >= TARGET_COMMENT:
            break
            
        if current_count == last_count:
            no_change += 1
        else:
            no_change = 0
            
        if no_change >= 3:
            print("no more comments")
            break
            
        last_count = current_count
        
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    comment_tags = soup.select("#content-text .ytAttributedStringHost")
    
    results = []
    seen = set()
    
    for comment_tag in comment_tags:
        text = parse_comment(comment_tag)
        if not text:
            continue
        if text in seen:
            continue
        seen.add(text)
        results.append({"content": text})
        
    results = results[:TARGET_COMMENT]
    
    with open(f"scraped/{video_id}_comments.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"saved {len(results)} comments for {video_id}")

driver.quit()
