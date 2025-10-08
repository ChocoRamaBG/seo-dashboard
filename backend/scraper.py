import logging
import time
import re
import os, signal, subprocess, tempfile, json, shutil
from pathlib import Path
from urllib.parse import unquote
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc

# ---------------- CONFIG ---------------- #
TARGET_CLASS = "sc-isexnS ispbmv"
TO_REMOVE = ["https", "www.", ":", "/"]
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "../data"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
XPATH_POPUP = "/html/body/div[26]/div/div/div[1]"
# ---------------------------------------- #

print("🚨 MAIN SCRAPER LOADED (LINUX RENDER MODE) 🚨")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def clean_website(url: str) -> str:
    for item in TO_REMOVE:
        url = url.replace(item, "")
    return url


def get_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")  # for linux chrome >= 115
    options.add_argument("--no-sandbox")  # mandatory in docker/linux
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--user-data-dir=/tmp/chrome_user_data")

    driver = uc.Chrome(options=options, headless=True)
    return driver


def scrape_site(website: str) -> Path:
    retries = 3
    last_exception = None
    TARGET_XPATH = '//*[@id="root"]/div[1]/div/div/div[3]/div/div[8]'

    for attempt in range(1, retries + 1):
        driver = get_driver()
        output_path = OUTPUT_DIR / f"{website}_neilpatel_data.txt"
        try:
            driver.set_page_load_timeout(45)
            logging.info(f"[Attempt {attempt}] Scraping website: {website}")
            driver.get(f"https://app.neilpatel.com/en/traffic_analyzer/overview?domain={website}")

            # Optional sleep for dynamic loading issues
            time.sleep(5)

            try:
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, XPATH_POPUP))
                )
                element.click()
                logging.info("Popup closed successfully.")
            except Exception:
                logging.debug("Popup not found or already closed.")

            WebDriverWait(driver, 25).until(
                EC.presence_of_element_located((By.XPATH, TARGET_XPATH))
            )

            element = driver.find_element(By.XPATH, TARGET_XPATH)
            text_content = element.text

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("===== STRUCTURED OUTPUT =====\n")
                f.write(text_content)
                f.write("\n\n")

            logging.info(f"Saved raw scrape to {output_path}")
            return output_path

        except Exception as e:
            last_exception = e
            logging.warning(f"Attempt {attempt} failed: {e}")
            time.sleep(3)
        finally:
            driver.quit()

    logging.error(f"All {retries} attempts failed. Raising last exception.")
    raise last_exception


def parse_data(input_file: Path) -> dict:
    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    data = {
        "Traffic Overview": {},
        "SEO Keywords Ranking": {},
        "Top SEO Pages": [],
        "Top Keywords": []
    }

    traffic_section = re.search(r"Traffic Overview\s*:\s*(.*?)SEO KEYWORDS RANKING", raw_text, re.S)
    if traffic_section:
        t_text = traffic_section.group(1)
        if m := re.search(r"(\S+\.digital)", t_text):
            data["Traffic Overview"]["Domain"] = m.group(1)
        if (org := re.search(r"ORGANIC\s*(\d+)", t_text)) and (paid := re.search(r"PAID\s*(\d+)", t_text)):
            data["Traffic Overview"]["Previous Month"] = {
                "TRAFFIC": {"ORGANIC": int(org.group(1)), "PAID": int(paid.group(1))}
            }
        if m := re.search(r"DOMAIN AUTHORITY\s*(\d+)", t_text):
            data["Traffic Overview"].setdefault("Previous Month", {})["Domain Authority"] = int(m.group(1))
        if m := re.search(r"BACKLINKS\s*(\d+)", t_text):
            data["Traffic Overview"].setdefault("Previous Month", {})["Backlinks"] = {"Total": int(m.group(1))}

    for title, url, visits in re.findall(r"([^\n]+)\n(buzzmaker\.digital[^\n]*)\n(\d+)", raw_text):
        data["Top SEO Pages"].append({
            "Title": title.strip(),
            "URL": url.strip(),
            "Est. Visits": int(visits),
            "Backlinks": 0
        })

    for keyword, volume, position, visits in re.findall(r"([^\n]+)\n(\d+)\n(\d+)\n(\d+)", raw_text):
        data["Top Keywords"].append({
            "Keyword": keyword.strip(),
            "Volume": int(volume),
            "Position": int(position),
            "Est. Visits": int(visits)
        })

    return data


def save_json(data: dict, filename: str):
    output_path = OUTPUT_DIR / filename
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    logging.info(f"Structured JSON saved to {output_path}")


def analyze(url: str) -> dict:
    logging.info(f"ANALYZE() CALLED for {url}")
    file_path = scrape_site(url)
    parsed = parse_data(file_path)
    return {
        "domain": parsed.get("Traffic Overview", {}).get("Domain", url),
        "traffic": {
            "organic": parsed.get("Traffic Overview", {}).get("Previous Month", {}).get("TRAFFIC", {}).get("ORGANIC", 0),
            "paid": parsed.get("Traffic Overview", {}).get("Previous Month", {}).get("TRAFFIC", {}).get("PAID", 0),
            "domainAuthority": parsed.get("Traffic Overview", {}).get("Previous Month", {}).get("Domain Authority", 0),
            "backlinksTotal": parsed.get("Traffic Overview", {}).get("Previous Month", {}).get("Backlinks", {}).get("Total", 0)
        },
        "topPages": [
            {
                "title": page.get("Title", ""),
                "url": unquote(page.get("URL", "")),
                "estVisits": page.get("Est. Visits", 0),
                "backlinks": page.get("Backlinks", 0)
            }
            for page in parsed.get("Top SEO Pages", [])
            if page.get("Title", "").lower() != "0"
        ],
        "topKeywords": [
            {
                "keyword": kw.get("Keyword", ""),
                "volume": kw.get("Volume", 0),
                "position": kw.get("Position", 0),
                "estVisits": kw.get("Est. Visits", 0)
            }
            for kw in parsed.get("Top Keywords", [])
            if kw.get("Keyword", "").lower() != "view all"
        ]
    }
