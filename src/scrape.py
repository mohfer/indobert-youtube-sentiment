from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from bs4 import BeautifulSoup
from bs4 import NavigableString

import time
import json
from pathlib import Path

VIDEO_URL = "https://www.youtube.com/watch?v=0J-g47xMUms"

VIDEO_ID = VIDEO_URL.split("v=")[-1]

TARGET_COMMENT = 200

options = Options()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--user-agent=Mozilla/5.0")

driver = webdriver.Chrome(options=options)

driver.get(VIDEO_URL)

print("Loading page...")

time.sleep(5)

driver.execute_script(
    "window.scrollTo(0, 3000);"
)

time.sleep(3)

last_count = 0
no_change = 0

for i in range(30):

    driver.execute_script(
        "window.scrollBy(0, 2000);"
    )

    time.sleep(2)

    comments = driver.find_elements(
        By.CSS_SELECTOR,
        "#content-text"
    )

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

comment_tags = soup.select(
    "#content-text .ytAttributedStringHost"
)

def parse_comment(tag):

    result = ""

    for child in tag.descendants:

        if isinstance(child, NavigableString):

            result += str(child)

        elif child.name == "img":

            result += child.get("alt", "")

    return result.strip()

results = []
seen = set()

for comment in comment_tags:

    text = parse_comment(comment)

    if not text:
        continue

    if text in seen:
        continue

    seen.add(text)

    results.append({
        "content": text
    })

results = results[:TARGET_COMMENT]

Path("scrape").mkdir(exist_ok=True)

with open(
    f"scrape/{VIDEO_ID}_comments.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        results,
        f,
        ensure_ascii=False,
        indent=2
    )

print(f"saved {len(results)} comments")

driver.quit()