import re
import json
import logging
import time
import requests
from pathlib import Path
from urllib.parse import unquote
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

TARGET_CLASS = "sc-isexnS ispbmv"
OUTPUT_DIR = Path("../data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

def clean_website(url: str) -> str:
    for part in ["https://", "http://", "www.", "/", ":"]:
        url = url.replace(part, "")
    return url

def lightweight_scrape(website: str) -> Path:
    output_path = OUTPUT_DIR / f"{website}_data.txt"
    url = f"https://app.neilpatel.com/en/traffic_analyzer/overview?domain={website}"
    logging.info(f"Fetching {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        text = soup.get_text(separator="\n")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        return output_path
    except Exception as e:
        logging.error(f"Scrape failed for {website}: {e}")
        raise

def parse_data(input_file: Path) -> dict:
    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    data = {
        "Traffic Overview": {},
        "SEO Keywords Ranking": {},
        "Top SEO Pages": [],
        "Top Keywords": []
    }

    traffic_section = re.search(r"Traffic Overview\s*([\s\S]*?)SEO", raw_text)
    if traffic_section:
        txt = traffic_section.group(1)
        if m := re.search(r"DOMAIN AUTHORITY\s*(\d+)", txt):
            data["Traffic Overview"]["Domain Authority"] = int(m.group(1))
        if m := re.search(r"BACKLINKS\s*(\d+)", txt):
            data["Traffic Overview"]["Backlinks"] = int(m.group(1))
        if (org := re.search(r"ORGANIC\s*(\d+)", txt)) and (paid := re.search(r"PAID\s*(\d+)", txt)):
            data["Traffic Overview"]["Traffic"] = {
                "ORGANIC": int(org.group(1)),
                "PAID": int(paid.group(1))
            }

    for title, url, visits in re.findall(r"([^\n]+)\n(https?://[^\n]+)\n(\d+)", raw_text):
        data["Top SEO Pages"].append({
            "Title": title.strip(),
            "URL": url.strip(),
            "Est. Visits": int(visits)
        })

    for kw, vol, pos, vis in re.findall(r"([^\n]+)\n(\d+)\n(\d+)\n(\d+)", raw_text):
        data["Top Keywords"].append({
            "Keyword": kw.strip(),
            "Volume": int(vol),
            "Position": int(pos),
            "Est. Visits": int(vis)
        })

    return data

def save_json(data: dict, filename: str):
    out = OUTPUT_DIR / filename
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info(f"Saved {out}")

def analyze(url: str) -> dict:
    domain = clean_website(url)
    path = lightweight_scrape(domain)
    parsed = parse_data(path)
    return {
        "domain": domain,
        "traffic": parsed.get("Traffic Overview", {}),
        "topPages": parsed.get("Top SEO Pages", []),
        "topKeywords": parsed.get("Top Keywords", [])
    }

if __name__ == "__main__":
    start = time.time()
    result = analyze("buzzmaker.digital")  # example
    save_json(result, "result.json")
    print(json.dumps(result, indent=2))
    print("Time:", round(time.time() - start, 2), "sec")
