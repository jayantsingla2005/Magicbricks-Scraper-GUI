# Let's also create a simpler, more focused scraper that specifically handles the MagicBricks URL structure
# This version will be more reliable for the specific site structure

simplified_scraper = '''
#!/usr/bin/env python3
"""
MagicBricks Gurgaon Property Scraper
A focused scraper designed specifically for MagicBricks property listings.
Handles all 30K+ listings with pagination and comprehensive data extraction.
"""

import requests
import pandas as pd
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging
from urllib.parse import urljoin
import random
import json

class MagicBricksScraperV2:
    def __init__(self):
        self.properties = []
        self.setup_logging()
        self.setup_driver()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraper.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_driver(self):
        """Setup Chrome driver with optimal settings for MagicBricks"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def extract_property_info(self, property_card):
        """Extract all relevant information from a property card"""
        data = {
            'title': '',
            'price': '',
            'price_per_sqft': '',
            'area': '',
            'bedrooms': '',
            'bathrooms': '',
            'floor': '',
            'age': '',
            'furnishing': '',
            'property_type': '',
            'locality': '',
            'society': '',
            'builder': '',
            'possession': '',
            'parking': '',
            'facing': '',
            'amenities': '',
            'description': '',
            'agent_name': '',
            'agent_contact': '',
            'property_url': '',
            'image_urls': '',
            'latitude': '',
            'longitude': '',
            'posted_date': '',
            'property_id': ''
        }
        
        try:
            # Title
            title_elem = property_card.find('h2') or property_card.find('h3') or property_card.find('a', class_=re.compile('title', re.I))
            if title_elem:
                data['title'] = title_elem.get_text(strip=True)
                
            # Property URL
            url_elem = property_card.find('a', href=True)
            if url_elem:
                data['property_url'] = urljoin('https://www.magicbricks.com', url_elem['href'])
                # Extract property ID from URL
                url_parts = url_elem['href'].split('/')
                for part in url_parts:
                    if 'property' in part.lower() or part.isdigit():
                        data['property_id'] = part
                        break
                        
            # Price
            price_elem = property_card.find(text=re.compile(r'₹.*(?:crore|lakh)', re.I))
            if not price_elem:
                price_elem = property_card.find(class_=re.compile('price', re.I))
            if price_elem:
                if hasattr(price_elem, 'get_text'):
                    data['price'] = price_elem.get_text(strip=True)
                else:
                    data['price'] = str(price_elem).strip()
                    
            # Area
            area_elem = property_card.find(text=re.compile(r'\\d+.*sqft', re.I))
            if area_elem:
                area_match = re.search(r'(\\d+(?:,\\d+)?)', str(area_elem))
                if area_match:
                    data['area'] = area_match.group(1)
                    
            # Bedrooms
            bed_elem = property_card.find(text=re.compile(r'\\d+\\s*(?:bhk|bed)', re.I))
            if bed_elem:
                bed_match = re.search(r'(\\d+)', str(bed_elem))
                if bed_match:
                    data['bedrooms'] = bed_match.group(1)
                    
            # Bathrooms  
            bath_elem = property_card.find(text=re.compile(r'\\d+\\s*bath', re.I))
            if bath_elem:
                bath_match = re.search(r'(\\d+)', str(bath_elem))
                if bath_match:
                    data['bathrooms'] = bath_match.group(1)
                    
            # Location/Locality
            location_elem = property_card.find(class_=re.compile('location|address', re.I))
            if location_elem:
                data['locality'] = location_elem.get_text(strip=True)
                
            # Property type
            type_elem = property_card.find(text=re.compile(r'apartment|villa|house|plot|floor', re.I))
            if type_elem:
                data['property_type'] = str(type_elem).strip()
                
            # Images
            images = property_card.find_all('img')
            image_urls = []
            for img in images:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and 'http' in src:
                    image_urls.append(src)
            data['image_urls'] = '|'.join(image_urls)
            
            # Additional details from spans and divs
            all_text = property_card.get_text(separator=' ', strip=True)
            
            # Floor information
            floor_match = re.search(r'(\\d+)(?:st|nd|rd|th)?\\s*floor', all_text, re.I)
            if floor_match:
                data['floor'] = floor_match.group(1)
                
            # Age
            age_match = re.search(r'(\\d+)\\s*(?:year|yr)s?\\s*old', all_text, re.I)
            if age_match:
                data['age'] = age_match.group(1)
                
            # Furnishing
            if 'furnished' in all_text.lower():
                if 'semi' in all_text.lower():
                    data['furnishing'] = 'Semi Furnished'
                elif 'un' in all_text.lower() or 'not' in all_text.lower():
                    data['furnishing'] = 'Unfurnished'
                else:
                    data['furnishing'] = 'Furnished'
                    
            # Parking
            parking_match = re.search(r'(\\d+)\\s*(?:car|parking)', all_text, re.I)
            if parking_match:
                data['parking'] = parking_match.group(1)
                
        except Exception as e:
            self.logger.error(f"Error extracting property info: {e}")
            
        return data
    
    def scrape_page(self, url, page_num):
        """Scrape a single page of listings"""
        self.logger.info(f"Scraping page {page_num}: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(random.uniform(3, 6))
            
            # Wait for content to load
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find property cards using multiple selectors
            property_cards = []
            selectors = [
                '[class*="mb-srp"]',
                '[class*="propertyCard"]',
                '[class*="property-card"]',
                '[class*="SRPTuple"]',
                '[class*="result"]',
                'div[data-id]'
            ]
            
            for selector in selectors:
                cards = soup.select(selector)
                if cards and len(cards) > 5:  # Reasonable number of properties
                    property_cards = cards
                    self.logger.info(f"Found {len(cards)} properties using selector: {selector}")
                    break
            
            if not property_cards:
                # Fallback: look for divs that might contain property data
                property_cards = soup.find_all('div', class_=re.compile(r'mb-srp|property|card', re.I))
                
            page_properties = []
            for card in property_cards:
                prop_data = self.extract_property_info(card)
                if prop_data['title'] or prop_data['price']:  # Only add if we have meaningful data
                    page_properties.append(prop_data)
                    
            self.logger.info(f"Extracted {len(page_properties)} properties from page {page_num}")
            return page_properties
            
        except Exception as e:
            self.logger.error(f"Error scraping page {page_num}: {e}")
            return []
    
    def get_total_pages(self, base_url):
        """Get total number of pages to scrape"""
        try:
            self.driver.get(base_url)
            time.sleep(3)
            
            # Look for pagination or total results
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Try to find total results count
            result_count_elem = soup.find(text=re.compile(r'\\d+.*(?:result|propert)', re.I))
            if result_count_elem:
                count_match = re.search(r'(\\d+(?:,\\d+)*)', str(result_count_elem))
                if count_match:
                    total_results = int(count_match.group(1).replace(',', ''))
                    # Assuming ~20 properties per page
                    estimated_pages = (total_results // 20) + 1
                    self.logger.info(f"Estimated {total_results} total properties across ~{estimated_pages} pages")
                    return min(estimated_pages, 2000)  # Cap at reasonable number
            
            # Fallback: look for last page number in pagination
            page_links = soup.find_all('a', href=re.compile(r'page[=-]\\d+', re.I))
            if page_links:
                max_page = 1
                for link in page_links:
                    page_match = re.search(r'page[=-](\\d+)', link.get('href', ''), re.I)
                    if page_match:
                        max_page = max(max_page, int(page_match.group(1)))
                if max_page > 1:
                    self.logger.info(f"Found pagination with {max_page} pages")
                    return max_page
            
            # Default assumption
            self.logger.warning("Could not determine total pages, using default estimate")
            return 1500  # Conservative estimate for 30K properties
            
        except Exception as e:
            self.logger.error(f"Error determining total pages: {e}")
            return 1500
    
    def scrape_all_properties(self, base_url="https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs"):
        """Main scraping function"""
        self.logger.info("Starting MagicBricks Gurgaon property scraping...")
        
        # Get total pages
        total_pages = self.get_total_pages(base_url)
        
        scraped_count = 0
        failed_pages = 0
        
        for page in range(1, total_pages + 1):
            # Build URL for current page
            if '?' in base_url:
                page_url = f"{base_url}&page={page}"
            else:
                page_url = f"{base_url}?page={page}"
            
            # Scrape the page
            page_properties = self.scrape_page(page_url, page)
            
            if page_properties:
                self.properties.extend(page_properties)
                scraped_count += len(page_properties)
                failed_pages = 0  # Reset failed counter
                
                self.logger.info(f"Progress: Page {page}/{total_pages}, Total properties: {scraped_count}")
                
                # Save checkpoint every 50 pages
                if page % 50 == 0:
                    self.save_checkpoint(f"checkpoint_page_{page}.csv")
                    
            else:
                failed_pages += 1
                self.logger.warning(f"No properties found on page {page}")
                
                # Stop if too many consecutive failures
                if failed_pages >= 10:
                    self.logger.info("Too many failed pages in a row. Stopping scraping.")
                    break
            
            # Random delay between pages
            time.sleep(random.uniform(2, 5))
        
        self.logger.info(f"Scraping completed! Total properties scraped: {len(self.properties)}")
    
    def save_checkpoint(self, filename):
        """Save current progress to CSV"""
        if self.properties:
            df = pd.DataFrame(self.properties)
            df.to_csv(filename, index=False, encoding='utf-8')
            self.logger.info(f"Checkpoint saved: {filename} ({len(df)} properties)")
    
    def save_to_csv(self, filename="magicbricks_gurgaon_properties_complete.csv"):
        """Save final results to CSV"""
        if not self.properties:
            self.logger.error("No properties to save!")
            return None
        
        df = pd.DataFrame(self.properties)
        
        # Remove duplicates based on property URL
        df = df.drop_duplicates(subset=['property_url'], keep='first')
        
        # Clean data
        df = df.fillna('')  # Replace NaN with empty strings
        
        # Save to CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        
        # Summary statistics
        self.logger.info(f"\\n=== SCRAPING SUMMARY ===")
        self.logger.info(f"Total properties scraped: {len(df)}")
        self.logger.info(f"Properties with prices: {(df['price'] != '').sum()}")
        self.logger.info(f"Properties with areas: {(df['area'] != '').sum()}")
        self.logger.info(f"Properties with images: {(df['image_urls'] != '').sum()}")
        self.logger.info(f"Unique localities: {df['locality'].nunique()}")
        self.logger.info(f"Data saved to: {filename}")
        
        return df
    
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            self.logger.info("WebDriver closed")

def main():
    """Main execution function"""
    scraper = MagicBricksScraperV2()
    
    try:
        # Start scraping
        scraper.scrape_all_properties()
        
        # Save results
        df = scraper.save_to_csv()
        
        if df is not None:
            print(f"\\nSuccess! Scraped {len(df)} properties from MagicBricks Gurgaon")
            print(f"Data saved to: magicbricks_gurgaon_properties_complete.csv")
            print("\\nColumns included:", list(df.columns))
        else:
            print("No data was scraped. Check the logs for errors.")
            
    except Exception as e:
        print(f"Scraping failed with error: {e}")
        
    finally:
        scraper.close()

if __name__ == "__main__":
    main()
'''

# Safe write guard to prevent accidental overwrite
import os, sys

ALLOW_OVERWRITE = False
TARGET_FILE = 'magicbricks_scraper_v2.py'

if os.path.exists(TARGET_FILE) and not ALLOW_OVERWRITE:
    print(f"Skip generation: {TARGET_FILE} already exists. Set ALLOW_OVERWRITE=True to regenerate.")
else:
    with open(TARGET_FILE, 'w', encoding='utf-8') as f:
        f.write(simplified_scraper)
    print(f"Improved MagicBricks scraper created: '{TARGET_FILE}'")