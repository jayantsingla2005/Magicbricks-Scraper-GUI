#!/usr/bin/env python3
"""
MagicBricks Gurgaon Property Scraper V2 - hardened
Enhanced with anti-detection, retries/backoff, configurable headless, proxy, and CLI flags.
"""

import argparse
import logging
import random
import re
import time
import csv
from typing import Optional, List, Dict
from urllib.parse import urljoin

# Optional pandas import with fallback to stdlib csv
try:
    import pandas as pd  # type: ignore
    PANDAS_AVAILABLE = True
except Exception:
    pd = None  # type: ignore
    PANDAS_AVAILABLE = False

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

UA_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]


class MagicBricksScraperV2:
    def __init__(
        self,
        headless: bool = True,
        delay_range: tuple = (2, 5),
        max_retries_per_page: int = 2,
        backoff_base: float = 2.0,
        backoff_cap: float = 20.0,
        proxy: Optional[str] = None,
        driver_path: Optional[str] = None,
        user_agents: Optional[List[str]] = None,
        checkpoint_interval: int = 50,
    ):
        self.properties: List[Dict] = []
        self.headless = headless
        self.delay_range = delay_range
        self.max_retries_per_page = max_retries_per_page
        self.backoff_base = backoff_base
        self.backoff_cap = backoff_cap
        self.proxy = proxy
        self.driver_path = driver_path
        self.user_agents = user_agents or UA_LIST
        self.checkpoint_interval = checkpoint_interval
        self.driver = None
        self.setup_logging()
        self.setup_driver()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def setup_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        # default UA
        chrome_options.add_argument(f"--user-agent={self.user_agents[0]}")
        if self.proxy:
            chrome_options.add_argument(f"--proxy-server={self.proxy}")

        # Prefer Selenium Manager (auto-resolves correct ChromeDriver) and fall back to webdriver-manager
        try:
            if self.driver_path:
                service = Service(self.driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Selenium Manager (Selenium 4.6+) automatically manages the correct driver binary
                self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            self.logger.warning(f"Selenium Manager failed ({e}); falling back to webdriver-manager")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
 
        # Stealth tweaks
        try:
            self.driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"},
            )
        except Exception:
            pass
        self.logger.info("WebDriver initialized")

    def _set_rotating_user_agent(self):
        try:
            ua = random.choice(self.user_agents)
            self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": ua})
        except Exception:
            # Fallback silently
            pass

    def _random_delay(self):
        time.sleep(random.uniform(self.delay_range[0], self.delay_range[1]))

    def extract_property_info(self, property_card):
        data = {
            "title": "",
            "price": "",
            "price_per_sqft": "",
            "carpet_area": "",
            "super_area": "",
            "area": "",
            "bedrooms": "",
            "bathrooms": "",
            "floor": "",
            "age": "",
            "furnishing": "",
            "property_type": "",
            "locality": "",
            "society": "",
            "builder": "",
            "possession": "",
            "parking": "",
            "facing": "",
            "amenities": "",
            "description": "",
            "agent_name": "",
            "agent_contact": "",
            "property_url": "",
            "image_urls": "",
            "latitude": "",
            "longitude": "",
            "posted_date": "",
            "property_id": "",
        }
        try:
            # Prefer data-id attribute
            if property_card and property_card.has_attr("data-id"):
                data["property_id"] = property_card.get("data-id", "").strip()

            # Title
            title_elem = property_card.find("h2") or property_card.find("h3") or property_card.find(
                "a", class_=re.compile("title", re.I)
            )
            if title_elem:
                data["title"] = title_elem.get_text(strip=True)

            # URL and property_id fallback (prefer anchors that look like property detail URLs)
            chosen_href = ""
            anchors = property_card.find_all("a", href=True)
            for a in anchors:
                href = a["href"]
                if re.search(r"(propertyDetails|property-for-|/sale/|/rent/)", href, re.I):
                    chosen_href = href
                    break
            if not chosen_href and anchors:
                # fallback: first anchor
                chosen_href = anchors[0]["href"]

            if chosen_href:
                data["property_url"] = urljoin("https://www.magicbricks.com", chosen_href)
                if not data["property_id"]:
                    m = re.search(r"(?:pid|id|listing|prop)[=/-](\d{5,})", chosen_href, re.I)
                    if m:
                        data["property_id"] = m.group(1)
                    else:
                        m2 = re.search(r"(\d{7,})", chosen_href)
                        if m2:
                            data["property_id"] = m2.group(1)

            # Price
            price_elem = property_card.select_one('[class*="price"]') or property_card.find(string=re.compile(r"₹|crore|lakh", re.I))
            if price_elem:
                data["price"] = price_elem.get_text(strip=True) if hasattr(price_elem, "get_text") else str(price_elem).strip()

            # Price per sqft
            pps_elem = (
                property_card.select_one('[class*="per"] [class*="sqft"], [class*="per-sqft"], [class*="price-per-sqft"]')
                or property_card.find(string=re.compile(r"₹\s*[\d,]+\s*(?:/|per)\s*(?:sq\.?\s*ft|sqft)", re.I))
            )
            if pps_elem:
                pps_text = pps_elem.get_text(strip=True) if hasattr(pps_elem, "get_text") else str(pps_elem).strip()
                data["price_per_sqft"] = pps_text

            # Areas
            all_text = property_card.get_text(separator=" ", strip=True)
            # carpet/super areas
            m_carpet = re.search(r"(?:carpet)\s*[:\-]?\s*([\d,]+)\s*(?:sq\.?\s*ft|sqft)", all_text, re.I)
            if m_carpet:
                data["carpet_area"] = m_carpet.group(1).replace(",", "")
            m_super = re.search(r"(?:super|built\s*up)\s*[:\-]?\s*([\d,]+)\s*(?:sq\.?\s*ft|sqft)", all_text, re.I)
            if m_super:
                data["super_area"] = m_super.group(1).replace(",", "")
            if not data["carpet_area"] and not data["super_area"]:
                m_area = re.search(r"([\d,]+)\s*(?:sq\.?\s*ft|sqft)", all_text, re.I)
                if m_area:
                    data["area"] = m_area.group(1).replace(",", "")

            # Bedrooms
            m_bed = re.search(r"(\d+)\s*(?:bhk|bed)", all_text, re.I)
            if m_bed:
                data["bedrooms"] = m_bed.group(1)
            elif data.get("title"):
                m_bed2 = re.search(r"(\d+)\s*bhk", data["title"], re.I)
                if m_bed2:
                    data["bedrooms"] = m_bed2.group(1)

            # Bathrooms
            m_bath = re.search(r"(\d+)\s*bath", all_text, re.I)
            if m_bath:
                data["bathrooms"] = m_bath.group(1)

            # Floor
            m_floor = re.search(r"(\d+)(?:st|nd|rd|th)?\s*floor", all_text, re.I)
            if m_floor:
                data["floor"] = m_floor.group(1)

            # Furnishing
            if "furnished" in all_text.lower():
                if "semi" in all_text.lower():
                    data["furnishing"] = "Semi Furnished"
                elif "un" in all_text.lower() or "not" in all_text.lower():
                    data["furnishing"] = "Unfurnished"
                else:
                    data["furnishing"] = "Furnished"

            # Location/locality
            location_elem = property_card.select_one('.mb-srp__card__location, .mb-srp__card__details--location, .SRPTuple__tupleComm')
            if not location_elem:
                location_elem = property_card.find(class_=re.compile("location|address", re.I))
            if location_elem:
                data["locality"] = location_elem.get_text(strip=True)
            # Fallback: derive locality from title or URL slug
            if not data["locality"]:
                src_text = (data.get("title") or "") + " " + (data.get("property_url") or "")
                m_loc = re.search(r"(sector\s*\d+[a-zA-Z]?(?:\s*[a-z]+)?)\s*gurgaon", src_text, re.I)
                if m_loc:
                    data["locality"] = m_loc.group(1).strip().title()
                else:
                    for kw in ["DLF Phase 1", "DLF Phase 2", "DLF Phase 3", "Golf Course Extension", "Palam Vihar", "Gwal Pahari", "Dwarka Expressway", "Sohna Road"]:
                        if re.search(kw, src_text, re.I):
                            data["locality"] = kw
                            break

            # Property type
            type_elem = property_card.find(string=re.compile(r"apartment|villa|house|plot|floor", re.I))
            if type_elem:
                data["property_type"] = str(type_elem).strip()

            # Images (filter out non-photo assets)
            images = property_card.find_all("img")
            image_urls = []

            def _add_img_url(u: str):
                u = str(u)
                if (
                    u.startswith("http")
                    and re.search(r"\.(jpg|jpeg|png|webp)(?:\?.*)?$", u, re.I)
                    and ("magicbricks" in u or "staticmb.com" in u or "mbphoto" in u or "mbstatic" in u or "img" in u)
                ):
                    image_urls.append(u)

            for img in images:
                src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
                if src:
                    _add_img_url(src)
                srcset = img.get("srcset") or img.get("data-srcset")
                if srcset:
                    # take first candidate
                    first = str(srcset).split(",")[0].strip().split(" ")[0]
                    if first:
                        _add_img_url(first)

            # De-duplicate
            image_urls = list(dict.fromkeys(image_urls))
            data["image_urls"] = "|".join(image_urls)
        except Exception as e:
            self.logger.error(f"Error extracting property info: {e}")
        return data

    def _wait_for_listing_container(self):
        selectors = [
            '[class*="mb-srp"]',
            '[class*="propertyCard"]',
            '[class*="property-card"]',
            '[class*="SRPTuple"]',
            '[class*="result"]',
            'div[data-id]',
        ]
        for sel in selectors:
            try:
                WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, sel)))
                return True
            except TimeoutException:
                continue
        return False

    def scrape_page(self, url, page_num):
        self.logger.info(f"Scraping page {page_num}: {url}")
        attempt = 0
        while attempt <= self.max_retries_per_page:
            try:
                self._set_rotating_user_agent()
                self.driver.get(url)
                # Wait for content container
                has_container = self._wait_for_listing_container()
                if not has_container:
                    raise TimeoutException("Listing container not found")

                soup = BeautifulSoup(self.driver.page_source, "html.parser")

                property_cards = []
                # Prefer specific tuple/card containers to avoid large non-card wrappers
                selectors = [
                    'li.mb-srp__list__item',
                    'div.mb-srp__card',
                    'div.SRPTuple__cardWrap',
                    'div.SRPTuple__card',
                    'div.SRPTuple__tupleWrap',
                    'article[class*="SRPTuple"]',
                    'div[data-id][data-listingid]',
                ]
                for selector in selectors:
                    cards = soup.select(selector)
                    # Heuristic: choose the first selector that yields a reasonable number of card elements
                    if cards and len(cards) >= 10:
                        property_cards = cards
                        self.logger.info(f"Found {len(cards)} properties using selector: {selector}")
                        break
                if not property_cards:
                    # Last resort: attempt a broader query but will filter later by property_url presence
                    property_cards = soup.select('div.mb-srp__card, div.SRPTuple__card, li.mb-srp__list__item')

                if not property_cards:
                    property_cards = soup.find_all("div", class_=re.compile(r"mb-srp|property|card", re.I))

                page_properties = []
                for card in property_cards:
                    prop_data = self.extract_property_info(card)
                    # Only accept if a property URL was detected to avoid wrapper duplicates
                    if prop_data.get("property_url"):
                        page_properties.append(prop_data)

                if page_properties:
                    self.logger.info(f"Extracted {len(page_properties)} properties from page {page_num}")
                    return page_properties
                else:
                    raise Exception("No properties parsed from page")
            except Exception as e:
                self.logger.warning(f"Attempt {attempt+1}/{self.max_retries_per_page+1} failed for page {page_num}: {e}")
                attempt += 1
                if attempt > self.max_retries_per_page:
                    break
                backoff = min(self.backoff_base ** attempt, self.backoff_cap)
                time.sleep(backoff + random.uniform(self.delay_range[0], self.delay_range[1]))
        return []

    def get_total_pages(self, base_url):
        try:
            self._set_rotating_user_agent()
            self.driver.get(base_url)
            self._wait_for_listing_container()
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            result_count_elem = soup.find(string=re.compile(r"\d+.*(?:result|propert)", re.I))
            if result_count_elem:
                count_match = re.search(r"(\d+(?:,\d+)*)", str(result_count_elem))
                if count_match:
                    total_results = int(count_match.group(1).replace(",", ""))
                    estimated_pages = (total_results // 20) + 1
                    self.logger.info(f"Estimated {total_results} total properties across ~{estimated_pages} pages")
                    return min(estimated_pages, 2000)

            page_links = soup.find_all("a", href=re.compile(r"page[=-]\d+", re.I))
            if page_links:
                max_page = 1
                for link in page_links:
                    page_match = re.search(r"page[=-](\d+)", link.get("href", ""), re.I)
                    if page_match:
                        max_page = max(max_page, int(page_match.group(1)))
                if max_page > 1:
                    self.logger.info(f"Found pagination with {max_page} pages")
                    return max_page

            self.logger.warning("Could not determine total pages, using default estimate 1500")
            return 1500
        except Exception as e:
            self.logger.error(f"Error determining total pages: {e}")
            return 1500

    def scrape_all_properties(self, base_url="https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs", max_pages=None):
        self.logger.info("Starting MagicBricks Gurgaon property scraping...")
        total_pages = self.get_total_pages(base_url)
        if max_pages is not None:
            total_pages = min(total_pages, max_pages)

        scraped_count = 0
        failed_pages = 0
        for page in range(1, total_pages + 1):
            page_url = f"{base_url}&page={page}" if "?" in base_url else f"{base_url}?page={page}"

            page_properties = self.scrape_page(page_url, page)
            if page_properties:
                self.properties.extend(page_properties)
                scraped_count += len(page_properties)
                failed_pages = 0
                self.logger.info(f"Progress: Page {page}/{total_pages}, Total properties: {scraped_count}")

                if page % self.checkpoint_interval == 0:
                    self.save_checkpoint(f"checkpoint_page_{page}.csv")
            else:
                failed_pages += 1
                self.logger.warning(f"No properties found on page {page}")
                if failed_pages >= 10:
                    self.logger.info("Too many failed pages in a row. Stopping scraping.")
                    break

            self._random_delay()

        self.logger.info(f"Scraping completed! Total properties scraped: {len(self.properties)}")

    def save_checkpoint(self, filename):
        if not self.properties:
            return
        if PANDAS_AVAILABLE:
            df = pd.DataFrame(self.properties)  # type: ignore
            df.to_csv(filename, index=False, encoding="utf-8")
            self.logger.info(f"Checkpoint saved: {filename} ({len(df)} properties)")
        else:
            # Stdlib CSV write
            fieldnames = self._collect_fieldnames(self.properties)
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in self.properties:
                    writer.writerow(row)
            self.logger.info(f"Checkpoint saved (csv module): {filename} ({len(self.properties)} properties)")

    def _collect_fieldnames(self, rows: List[Dict]) -> List[str]:
        field_set = set()
        for r in rows:
            field_set.update(r.keys())
        # Prefer a stable order with commonly expected columns first
        preferred = [
            "property_id", "title", "price", "price_per_sqft",
            "carpet_area", "super_area", "area",
            "bedrooms", "bathrooms", "floor", "age",
            "furnishing", "parking", "facing", "property_type",
            "locality", "society", "builder", "possession",
            "amenities", "description", "agent_name", "agent_contact",
            "property_url", "image_urls", "latitude", "longitude",
            "posted_date"
        ]
        ordered = [c for c in preferred if c in field_set]
        for c in sorted(field_set):
            if c not in ordered:
                ordered.append(c)
        return ordered

    def save_to_csv(self, filename="magicbricks_gurgaon_properties_complete.csv"):
        if not self.properties:
            self.logger.error("No properties to save!")
            return None

        # Deduplicate by property_url regardless of pandas availability
        seen = set()
        deduped: List[Dict] = []
        for row in self.properties:
            key = row.get("property_url", "")
            if key and key not in seen:
                seen.add(key)
                deduped.append(row)

        if PANDAS_AVAILABLE:
            df = pd.DataFrame(deduped)  # type: ignore
            df = df.fillna("")
            df.to_csv(filename, index=False, encoding="utf-8")

            self.logger.info("\n=== SCRAPING SUMMARY ===")
            self.logger.info(f"Total properties scraped: {len(df)}")
            self.logger.info(f"Properties with prices: {(df['price'] != '').sum() if 'price' in df.columns else 0}")
            # Combined area count across carpet_area and area
            area_count = 0
            if 'carpet_area' in df.columns or 'area' in df.columns:
                ca = (df['carpet_area'] != '') if 'carpet_area' in df.columns else 0
                ar = (df['area'] != '') if 'area' in df.columns else 0
                area_count = (ca | ar).sum() if isinstance(ca, pd.Series) and isinstance(ar, pd.Series) else (ca if isinstance(ca, int) else ar.sum())
            self.logger.info(f"Properties with areas: {area_count}")
            self.logger.info(f"Properties with images: {(df['image_urls'] != '').sum() if 'image_urls' in df.columns else 0}")
            if "locality" in df.columns:
                self.logger.info(f"Unique localities: {df['locality'].replace('', pd.NA).dropna().nunique()}")
            self.logger.info(f"Data saved to: {filename}")
            return df
        else:
            # Stdlib CSV write
            fieldnames = self._collect_fieldnames(deduped)
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in deduped:
                    writer.writerow({k: ("" if v is None else v) for k, v in row.items()})
            # Log summary
            self.logger.info("\n=== SCRAPING SUMMARY (csv module) ===")
            self.logger.info(f"Total properties scraped: {len(deduped)}")
            price_count = sum(1 for r in deduped if r.get("price", ""))
            area_count = sum(1 for r in deduped if r.get("carpet_area", "") or r.get("area", ""))
            img_count = sum(1 for r in deduped if r.get("image_urls", ""))
            loc_set = set(r.get("locality", "") for r in deduped if r.get("locality", ""))
            self.logger.info(f"Properties with prices: {price_count}")
            self.logger.info(f"Properties with areas: {area_count}")
            self.logger.info(f"Properties with images: {img_count}")
            self.logger.info(f"Unique localities: {len(loc_set)}")
            self.logger.info(f"Data saved to: {filename}")
            return None  # No pandas DataFrame to return

    def close(self):
        if getattr(self, "driver", None):
            try:
                self.driver.quit()
            finally:
                self.logger.info("WebDriver closed")


def main():
    parser = argparse.ArgumentParser(description="MagicBricks Gurgaon Property Scraper (hardened v2)")
    parser.add_argument("--base-url", default="https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs")
    parser.add_argument("--max-pages", type=int, default=None)
    parser.add_argument("--headless", dest="headless", action="store_true", default=True, help="Run in headless mode (default)")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Run with visible browser")
    parser.add_argument("--delay-min", type=float, default=2.0)
    parser.add_argument("--delay-max", type=float, default=5.0)
    parser.add_argument("--retries", type=int, default=2, help="Max retries per page")
    parser.add_argument("--backoff-base", type=float, default=2.0)
    parser.add_argument("--backoff-cap", type=float, default=20.0)
    parser.add_argument("--proxy", type=str, default=None, help="http://host:port or socks5://host:port")
    parser.add_argument("--driver-path", type=str, default=None, help="Path to local ChromeDriver")
    parser.add_argument("--checkpoint-interval", type=int, default=50)
    args = parser.parse_args()

    scraper = MagicBricksScraperV2(
        headless=args.headless,
        delay_range=(args.delay_min, args.delay_max),
        max_retries_per_page=args.retries,
        backoff_base=args.backoff_base,
        backoff_cap=args.backoff_cap,
        proxy=args.proxy,
        driver_path=args.driver_path,
        checkpoint_interval=args.checkpoint_interval,
    )
    try:
        scraper.scrape_all_properties(base_url=args.base_url, max_pages=args.max_pages)
        df = scraper.save_to_csv()
        if df is not None:
            print(f"\nSuccess! Scraped {len(df)} properties from MagicBricks")
            print(f"Data saved to: magicbricks_gurgaon_properties_complete.csv")
            print("\nColumns included:", list(df.columns))
        else:
            print("Saved CSV using csv module. Check logs for summary counts.")
    except Exception as e:
        print(f"Scraping failed with error: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
