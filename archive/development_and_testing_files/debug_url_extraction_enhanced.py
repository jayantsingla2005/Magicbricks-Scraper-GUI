#!/usr/bin/env python3
"""
Enhanced Debug Script for URL Extraction Issues
This script uses the same anti-bot detection strategies as the main scraper
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from bs4 import BeautifulSoup
import time
import random

def debug_url_extraction():
    print("=== Enhanced URL Extraction Debug ===")
    
    # Initialize scraper with proper parameters
    scraper = IntegratedMagicBricksScraper(
        headless=False,  # Run in visible mode to see what's happening
        incremental_enabled=False  # Disable incremental for debugging
    )
    
    try:
        # Setup driver with anti-bot measures
        print("Setting up WebDriver with anti-bot measures...")
        scraper.setup_driver()
        
        if not scraper.driver:
            print("ERROR: Failed to initialize WebDriver")
            return
            
        # Test URL - using the same search URL format as the main scraper
        search_url = "https://www.magicbricks.com/property-for-sale/residential-real-estate?bedroom=1,2,3,4,5%2B&proptype=Multistorey-Apartment,Builder-Floor,Penthouse,Studio-Apartment&cityName=Gurgaon"
        
        print(f"Navigating to: {search_url}")
        
        # Add random delay before navigation
        delay = random.uniform(2, 5)
        print(f"Waiting {delay:.1f} seconds before navigation...")
        time.sleep(delay)
        
        # Navigate with error handling
        try:
            scraper.driver.get(search_url)
            time.sleep(3)  # Wait for page load
            
            # Check for bot detection
            page_source = scraper.driver.page_source.lower()
            if any(indicator in page_source for indicator in ['access denied', 'bot', 'captcha', 'cloudflare']):
                print("WARNING: Bot detection detected in page source")
                
                # Save page source for inspection
                with open('debug_bot_detection.html', 'w', encoding='utf-8') as f:
                    f.write(scraper.driver.page_source)
                print("Page source saved to debug_bot_detection.html")
                
                # Try recovery strategy
                print("Applying bot detection recovery...")
                scraper._handle_bot_detection()
                
                # Try again
                time.sleep(5)
                scraper.driver.get(search_url)
                time.sleep(3)
            
            # Now try to find property cards using the same selectors as the main scraper
            print("\nSearching for property cards...")
            
            # Use the same property card selectors from the main scraper
            property_selectors = [
                'div[data-testid="srp-tuple"]',
                'div.mb-srp__card',
                'div.mb-srp__list__item',
                'div[class*="srp-tuple"]',
                'div[class*="mb-srp"]'
            ]
            
            property_cards = []
            for selector in property_selectors:
                cards = scraper.driver.find_elements("css selector", selector)
                if cards:
                    print(f"Found {len(cards)} property cards using selector: {selector}")
                    property_cards = cards
                    break
            
            if not property_cards:
                print("No property cards found with any selector")
                # Save page source for inspection
                with open('debug_no_cards.html', 'w', encoding='utf-8') as f:
                    f.write(scraper.driver.page_source)
                print("Page source saved to debug_no_cards.html")
                return
            
            print(f"\nAnalyzing first 5 property cards out of {len(property_cards)}...")
            
            # Test URL extraction on first 5 cards
            for i, card in enumerate(property_cards[:5]):
                print(f"\n--- Property Card {i+1} ---")
                
                # Get card HTML
                card_html = card.get_attribute('outerHTML')
                soup = BeautifulSoup(card_html, 'html.parser')
                
                # Test the same URL selectors used in _extract_property_url
                url_selectors = [
                    'a[href*="/propertydetail/"]',
                    'a[href*="/property-details/"]', 
                    'a[href*="magicbricks.com"]',
                    'a[href]'
                ]
                
                found_url = None
                for selector in url_selectors:
                    links = soup.select(selector)
                    if links:
                        href = links[0].get('href', '')
                        if href and ('propertydetail' in href or 'property-details' in href or 'magicbricks.com' in href):
                            found_url = href
                            print(f"  ✓ Found URL with selector '{selector}': {href[:100]}...")
                            break
                        else:
                            print(f"  ✗ Found link with selector '{selector}' but invalid: {href[:50]}...")
                    else:
                        print(f"  ✗ No links found with selector: {selector}")
                
                if not found_url:
                    print(f"  ❌ NO VALID URL FOUND for card {i+1}")
                    
                    # Save this card's HTML for detailed inspection
                    with open(f'debug_card_{i+1}_no_url.html', 'w', encoding='utf-8') as f:
                        f.write(card_html)
                    print(f"  Card HTML saved to debug_card_{i+1}_no_url.html")
                    
                    # Show all links in this card
                    all_links = soup.find_all('a')
                    print(f"  All links in card ({len(all_links)} total):")
                    for j, link in enumerate(all_links[:3]):  # Show first 3 links
                        href = link.get('href', 'NO_HREF')
                        text = link.get_text(strip=True)[:30]
                        print(f"    Link {j+1}: {href[:60]}... (text: '{text}')")
                else:
                    print(f"  ✅ SUCCESS: Found valid URL for card {i+1}")
            
            print("\n=== Debug Summary ===")
            print(f"Total property cards found: {len(property_cards)}")
            print("Check the saved HTML files for detailed inspection")
            
        except Exception as e:
            print(f"ERROR during navigation: {e}")
            # Save page source if available
            try:
                with open('debug_navigation_error.html', 'w', encoding='utf-8') as f:
                    f.write(scraper.driver.page_source)
                print("Page source saved to debug_navigation_error.html")
            except:
                pass
    
    except Exception as e:
        print(f"ERROR: {e}")
    
    finally:
        # Clean up
        try:
            if scraper.driver:
                scraper.driver.quit()
                print("\nWebDriver closed")
        except:
            pass

if __name__ == "__main__":
    debug_url_extraction()