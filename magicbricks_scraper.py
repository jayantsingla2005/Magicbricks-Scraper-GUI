
import requests
import pandas as pd
import time
import csv
import json
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import logging
from urllib.parse import urljoin, urlparse
import random

class MagicBricksScraper:
    """
    A comprehensive scraper for MagicBricks property listings.
    Handles pagination, all property fields, and exports to CSV.
    """

    def __init__(self, base_url, headless=True, delay_range=(2, 5)):
        """
        Initialize the MagicBricks scraper

        Args:
            base_url (str): Base URL for property search
            headless (bool): Run browser in headless mode
            delay_range (tuple): Random delay range between requests
        """
        self.base_url = base_url
        self.delay_range = delay_range
        self.properties_data = []
        self.total_scraped = 0

        # Setup logging
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        # Setup Chrome driver options
        self.chrome_options = Options()
        if headless:
            self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--window-size=1920,1080")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)

        # User agent to avoid detection
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.chrome_options.add_argument(f"--user-agent={user_agent}")

        self.driver = None

    def start_driver(self):
        """Initialize Chrome WebDriver"""
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise

    def random_delay(self):
        """Add random delay between requests to avoid being blocked"""
        delay = random.uniform(self.delay_range[0], self.delay_range[1])
        time.sleep(delay)

    def extract_property_data(self, property_element):
        """
        Extract comprehensive property data from a property element

        Args:
            property_element: BeautifulSoup element containing property data

        Returns:
            dict: Dictionary containing all property fields
        """
        property_data = {
            'title': None,
            'price': None,
            'price_per_sqft': None,
            'carpet_area': None,
            'super_area': None,
            'bedrooms': None,
            'bathrooms': None,
            'floor': None,
            'total_floors': None,
            'age': None,
            'furnishing': None,
            'parking': None,
            'facing': None,
            'property_type': None,
            'locality': None,
            'city': None,
            'builder': None,
            'society': None,
            'possession_status': None,
            'description': None,
            'amenities': None,
            'contact_number': None,
            'agent_name': None,
            'property_url': None,
            'image_urls': [],
            'latitude': None,
            'longitude': None,
            'posted_date': None,
            'property_id': None
        }

        try:
            # Property ID and URL
            property_link = property_element.find('a', href=True)
            if property_link:
                property_data['property_url'] = urljoin('https://www.magicbricks.com', property_link['href'])
                # Extract property ID from URL
                url_parts = property_link['href'].split('/')
                for part in url_parts:
                    if part.startswith('property'):
                        property_data['property_id'] = part
                        break

            # Title
            title_elem = property_element.find(['h2', 'h3'], class_=re.compile(r'.*title.*', re.I))
            if not title_elem:
                title_elem = property_element.find('a', class_=re.compile(r'.*title.*', re.I))
            if title_elem:
                property_data['title'] = title_elem.get_text(strip=True)

            # Price
            price_elem = property_element.find(class_=re.compile(r'.*price.*', re.I))
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                property_data['price'] = self.clean_price(price_text)

            # Price per sqft
            price_sqft_elem = property_element.find(text=re.compile(r'₹.*sqft', re.I))
            if price_sqft_elem:
                property_data['price_per_sqft'] = price_sqft_elem.strip()

            # Property details (area, beds, baths, etc.)
            detail_elements = property_element.find_all(class_=re.compile(r'.*detail.*|.*spec.*|.*info.*', re.I))
            for elem in detail_elements:
                text = elem.get_text(strip=True).lower()

                if 'sqft' in text or 'sq ft' in text:
                    if 'carpet' in text:
                        property_data['carpet_area'] = self.extract_area(text)
                    elif 'super' in text or 'built' in text:
                        property_data['super_area'] = self.extract_area(text)
                    elif not property_data['carpet_area'] and not property_data['super_area']:
                        property_data['carpet_area'] = self.extract_area(text)

                if 'bhk' in text or 'bed' in text:
                    property_data['bedrooms'] = self.extract_number(text)

                if 'bath' in text or 'toilet' in text:
                    property_data['bathrooms'] = self.extract_number(text)

                if 'floor' in text:
                    floor_match = re.search(r'(\d+).*floor', text)
                    if floor_match:
                        property_data['floor'] = floor_match.group(1)

            # Location
            location_elem = property_element.find(class_=re.compile(r'.*location.*|.*address.*', re.I))
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                property_data['locality'] = location_text
                if 'gurgaon' in location_text.lower():
                    property_data['city'] = 'Gurgaon'

            # Property type
            type_elem = property_element.find(text=re.compile(r'apartment|villa|house|plot|floor', re.I))
            if type_elem:
                property_data['property_type'] = type_elem.strip()

            # Images
            img_elements = property_element.find_all('img')
            for img in img_elements:
                if img.get('src'):
                    property_data['image_urls'].append(img['src'])
                elif img.get('data-src'):
                    property_data['image_urls'].append(img['data-src'])

            # Convert image URLs list to string for CSV
            property_data['image_urls'] = '|'.join(property_data['image_urls']) if property_data['image_urls'] else None

        except Exception as e:
            self.logger.error(f"Error extracting property data: {e}")

        return property_data

    def clean_price(self, price_text):
        """Clean and standardize price text"""
        if not price_text:
            return None

        # Remove currency symbols and extra spaces
        cleaned = re.sub(r'[₹$,]', '', price_text)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()

        # Convert crore, lakh to numbers
        if 'crore' in cleaned.lower():
            number_match = re.search(r'([\d.]+)', cleaned)
            if number_match:
                return f"{number_match.group(1)} Crore"
        elif 'lakh' in cleaned.lower():
            number_match = re.search(r'([\d.]+)', cleaned)
            if number_match:
                return f"{number_match.group(1)} Lakh"

        return cleaned

    def extract_area(self, text):
        """Extract area from text"""
        area_match = re.search(r'([\d,]+)\s*(?:sqft|sq\.?\s*ft)', text, re.I)
        if area_match:
            return area_match.group(1).replace(',', '')
        return None

    def extract_number(self, text):
        """Extract number from text"""
        number_match = re.search(r'(\d+)', text)
        if number_match:
            return number_match.group(1)
        return None

    def scrape_page(self, page_url):
        """
        Scrape a single page of property listings

        Args:
            page_url (str): URL of the page to scrape

        Returns:
            list: List of property data dictionaries
        """
        try:
            self.logger.info(f"Scraping page: {page_url}")
            self.driver.get(page_url)

            # Wait for page to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Additional wait for dynamic content
            time.sleep(3)

            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Find property containers - multiple possible selectors
            property_containers = []
            possible_selectors = [
                '[class*="propertyCard"]',
                '[class*="property-card"]',
                '[class*="result-item"]',
                '[class*="listing"]',
                '.mb-srp__list__item',
                '.mb-srp__card',
                '.SRPTuple__tupleMobile',
                '[data-id]'
            ]

            for selector in possible_selectors:
                containers = soup.select(selector)
                if containers:
                    property_containers = containers
                    self.logger.info(f"Found {len(containers)} properties using selector: {selector}")
                    break

            if not property_containers:
                # Fallback: look for any div that might contain property data
                property_containers = soup.find_all('div', class_=re.compile(r'.*property.*|.*card.*|.*item.*', re.I))
                self.logger.warning(f"Using fallback selector, found {len(property_containers)} potential containers")

            page_properties = []

            for container in property_containers:
                property_data = self.extract_property_data(container)
                # Only add if we got some meaningful data
                if property_data['title'] or property_data['price']:
                    page_properties.append(property_data)

            self.logger.info(f"Successfully extracted {len(page_properties)} properties from this page")
            return page_properties

        except TimeoutException:
            self.logger.error(f"Timeout while loading page: {page_url}")
            return []
        except Exception as e:
            self.logger.error(f"Error scraping page {page_url}: {e}")
            return []

    def find_next_page_url(self):
        """Find URL for next page of results"""
        try:
            # Look for next page button/link
            next_selectors = [
                'a[class*="next"]',
                'a[href*="page"]',
                '.pagination a:contains("Next")',
                '[class*="paging"] a:last-child'
            ]

            for selector in next_selectors:
                next_links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for link in next_links:
                    if link.is_enabled() and link.get_attribute('href'):
                        return link.get_attribute('href')

            # Alternative: look for page numbers and increment
            current_url = self.driver.current_url
            page_match = re.search(r'page[=-](\d+)', current_url)
            if page_match:
                current_page = int(page_match.group(1))
                next_page_url = current_url.replace(f'page={current_page}', f'page={current_page + 1}')
                return next_page_url
            else:
                # Add page parameter if not present
                if '?' in current_url:
                    return f"{current_url}&page=2"
                else:
                    return f"{current_url}?page=2"

        except Exception as e:
            self.logger.error(f"Error finding next page: {e}")
            return None

    def scrape_all_properties(self, max_pages=None):
        """
        Scrape all property listings from all pages

        Args:
            max_pages (int): Maximum number of pages to scrape (None for all)
        """
        if not self.driver:
            self.start_driver()

        current_url = self.base_url
        page_count = 0
        consecutive_empty_pages = 0

        while current_url and (max_pages is None or page_count < max_pages):
            page_count += 1
            self.logger.info(f"\n--- SCRAPING PAGE {page_count} ---")

            # Scrape current page
            page_properties = self.scrape_page(current_url)

            if page_properties:
                self.properties_data.extend(page_properties)
                self.total_scraped += len(page_properties)
                consecutive_empty_pages = 0
                self.logger.info(f"Total properties scraped so far: {self.total_scraped}")
            else:
                consecutive_empty_pages += 1
                self.logger.warning(f"No properties found on page {page_count}")

                # Stop if we hit too many empty pages in a row
                if consecutive_empty_pages >= 3:
                    self.logger.info("Too many consecutive empty pages. Stopping scraping.")
                    break

            # Find next page URL
            next_url = self.find_next_page_url()
            if next_url and next_url != current_url:
                current_url = next_url
                self.random_delay()  # Add delay between pages
            else:
                self.logger.info("No more pages found.")
                break

        self.logger.info(f"\nScraping completed! Total properties scraped: {self.total_scraped}")

    def save_to_csv(self, filename='magicbricks_gurgaon_properties.csv'):
        """
        Save scraped properties to CSV file

        Args:
            filename (str): Output CSV filename
        """
        if not self.properties_data:
            self.logger.warning("No data to save!")
            return

        # Convert to DataFrame
        df = pd.DataFrame(self.properties_data)

        # Clean and organize columns
        column_order = [
            'property_id', 'title', 'price', 'price_per_sqft', 'carpet_area', 'super_area',
            'bedrooms', 'bathrooms', 'floor', 'total_floors', 'age', 'furnishing',
            'parking', 'facing', 'property_type', 'locality', 'city', 'builder',
            'society', 'possession_status', 'description', 'amenities',
            'contact_number', 'agent_name', 'property_url', 'image_urls',
            'latitude', 'longitude', 'posted_date'
        ]

        # Reorder columns (keep existing columns even if not in order)
        existing_columns = [col for col in column_order if col in df.columns]
        other_columns = [col for col in df.columns if col not in column_order]
        final_columns = existing_columns + other_columns

        df = df[final_columns]

        # Save to CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        self.logger.info(f"Data saved to {filename}")
        self.logger.info(f"Total records: {len(df)}")
        self.logger.info(f"Columns: {list(df.columns)}")

        return df

    def get_summary_statistics(self):
        """Get summary statistics of scraped data"""
        if not self.properties_data:
            return "No data available"

        df = pd.DataFrame(self.properties_data)

        summary = {
            'total_properties': len(df),
            'properties_with_price': df['price'].notna().sum(),
            'properties_with_area': df['carpet_area'].notna().sum(),
            'unique_localities': df['locality'].nunique() if 'locality' in df.columns else 0,
            'property_types': df['property_type'].value_counts().to_dict() if 'property_type' in df.columns else {},
        }

        return summary

    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver closed")

# Usage example
def main():
    """Main function to run the scraper"""

    # URL for Gurgaon properties for sale
    base_url = "https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs"

    # Initialize scraper
    scraper = MagicBricksScraper(
        base_url=base_url,
        headless=True,  # Set to False to see browser in action
        delay_range=(3, 7)  # Random delay between 3-7 seconds
    )

    try:
        # Start scraping (limit to first 5 pages for testing)
        # Remove max_pages parameter to scrape all pages (30K+ listings)
        scraper.scrape_all_properties(max_pages=50)  # Adjust as needed

        # Save to CSV
        df = scraper.save_to_csv('magicbricks_gurgaon_all_properties.csv')

        # Print summary
        summary = scraper.get_summary_statistics()
        print("\nScraping Summary:")
        print(f"Total Properties: {summary['total_properties']}")
        print(f"Properties with Price: {summary['properties_with_price']}")
        print(f"Properties with Area: {summary['properties_with_area']}")
        print(f"Unique Localities: {summary['unique_localities']}")

        return df

    except Exception as e:
        print(f"Error during scraping: {e}")

    finally:
        # Always close the driver
        scraper.close_driver()

if __name__ == "__main__":
    df = main()
