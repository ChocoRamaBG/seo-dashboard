import logging
import asyncio
from pathlib import Path
from urllib.parse import unquote
import json
import re
from playwright.async_api import async_playwright

# ---------------- CONFIG ---------------- #
TO_REMOVE = ["https", "www.", ":", "/"]
OUTPUT_DIR = Path("../data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
XPATH_POPUP = "/html/body/div[26]/div/div/div[1]"
TARGET_XPATH = '//*[@id="root"]/div[1]/div/div/div[3]/div/div[8]'
# ---------------------------------------- #

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def clean_website(url: str) -> str:
    for item in TO_REMOVE:
        url = url.replace(item, "")
    return url

async def scrape_site(website: str) -> Path:
    output_path = OUTPUT_DIR / f"{website}_neilpatel_data.txt"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            url = f"https://app.neilpatel.com/en/traffic_analyzer/overview?domain={website}"
            logging.info(f"Scraping {url}")
            await page.goto(url, timeout=120_000)  # 120s timeout

            # Try closing popup if it exists
            try:
                popup = await page.wait_for_selector(XPATH_POPUP, timeout=5000)
                await popup.click()
                logging.info("Popup closed successfully.")
            except Exception:
                logging.debug("Popup not found or already closed.")

            # Wait for target element
            await page.wait_for_selector(TARGET_XPATH, timeout=60_000)
            element = await page.query_selector(TARGET_XPATH)
            text_content = await element.inner_text()

            with open(output_path, "w", encoding="utf-8") as f:
                f.write("===== STRUCTURED OUTPUT =====\n")
                f.write(text_content)
                f.write("\n\n")

            logging.info(f"Saved raw scrape to {output_path}")
            await browser.close()
            return output_path

        except Exception as e:
            logging.error(f"Scraping failed: {e}")
            await browser.close()
            raise e

# ---------------- Existing parse_data & save_json ---------------- #
# keep your parse_data(input_file: Path) and save_json(data, filename) exactly as before

# ---------------- FastAPI / frontend-ready wrapper ---------------- #
def analyze(url: str) -> dict:
    logging.info(f"ANALYZE() CALLED for {url}")
    file_path = asyncio.run(scrape_site(url))
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
