import logging
import time
import re
import os, signal, subprocess, tempfile
from selenium.webdriver.chrome.service import Service
import json
from pathlib import Path
import tempfile
from bs4 import BeautifulSoup
from pathlib import Path
import tempfile, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.edge.options import Options as EdgeOptions

# ---------------- CONFIG ---------------- #
TARGET_CLASS = "sc-isexnS ispbmv"
TO_REMOVE = ["https", "www.", ":", "/"]
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "../data"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
XPATH_POPUP = "/html/body/div[26]/div/div/div[1]"
# ---------------------------------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def clean_website(url: str) -> str:
    for item in TO_REMOVE:
        url = url.replace(item, "")
    return url



def kill_leftover_chrome():
    """Kill any leftover Chrome or chromedriver processes that might block new session."""
    try:
        if os.name == "nt":  # Windows
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["taskkill", "/F", "/IM", "chromedriver.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:  # Linux / Mac
            subprocess.run(["pkill", "-f", "chrome"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["pkill", "-f", "chromedriver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def get_driver():
    # убиваме всички Edge и msedgedriver, ако има
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["taskkill", "/F", "/IM", "msedgedriver.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    options = EdgeOptions()
    options.add_argument("--inprivate")  # еквивалент на incognito
    #options.add_argument("--headless=new")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    tmp_user_data_dir = tempfile.mkdtemp()
    options.add_argument(f"--user-data-dir={tmp_user_data_dir}")

    service = EdgeService("C:/WebDrivers/msedgedriver.exe")
    driver = webdriver.Edge(service=service, options=options)
    return driver, tmp_user_data_dir

def scrape_site(website: str) -> Path:
    retries = 3
    last_exception = None
    TARGET_XPATH = '//*[@id="root"]/div[1]/div/div/div[3]/div/div[7]'

    for attempt in range(1, retries + 1):
        driver, temp_dir = get_driver()
        output_path = OUTPUT_DIR / f"{website}_neilpatel_data.txt"
        try:
            driver.set_page_load_timeout(30)
            logging.info(f"[Attempt {attempt}] Scraping website: {website}")
            driver.get(f"https://app.neilpatel.com/en/traffic_analyzer/overview?domain={website}")

            # Close popup if exists
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, XPATH_POPUP))
                )
                element.click()
                logging.info("Popup closed successfully.")
            except Exception:
                logging.debug("Popup not found or already closed.")

            # Wait for target content using XPath
            WebDriverWait(driver, 20).until(
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
            time.sleep(2)  # chill 2 sec before retry

        finally:
            driver.quit()
            try:
                import shutil
                if temp_dir:
                    shutil.rmtree(temp_dir)
            except Exception as e:
                logging.warning(f"Could not remove temp dir {temp_dir}: {e}")

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

    # Traffic Overview
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

    # SEO Pages
    for title, url, visits in re.findall(r"([^\n]+)\n(buzzmaker\.digital[^\n]*)\n(\d+)", raw_text):
        data["Top SEO Pages"].append({
            "Title": title.strip(),
            "URL": url.strip(),
            "Est. Visits": int(visits),
            "Backlinks": 0
        })

    # Keywords
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

# ---------------- FastAPI / frontend-ready wrapper ---------------- #

def analyze(url: str) -> dict:
    """
    Обвива резултата от parse_data() в стабилна структура.
    Ако някое поле липсва, се връща 0 или празен масив.
    """
    # първо, извикай scrape_site за да създадеш файла
    file_path = scrape_site(url)
    
    # после парсни съдържанието
    parsed = parse_data(file_path)

    # върни го в frontend-ready форма
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
                "url": page.get("URL", ""),
                "estVisits": page.get("Est. Visits", 0),
                "backlinks": page.get("Backlinks", 0)
            }
            for page in parsed.get("Top SEO Pages", [])
        ],
        "topKeywords": [
            {
                "keyword": kw.get("Keyword", ""),
                "volume": kw.get("Volume", 0),
                "position": kw.get("Position", 0),
                "estVisits": kw.get("Est. Visits", 0)
            }
            for kw in parsed.get("Top Keywords", [])
        ]
    }

