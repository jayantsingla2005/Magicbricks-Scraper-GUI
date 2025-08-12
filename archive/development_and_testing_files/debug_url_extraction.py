#!/usr/bin/env python3
"""
Debug URL Extraction Issues
Analyzes the actual HTML structure of property cards to understand URL extraction problems
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from bs4 import BeautifulSoup
import requests
import time

def debug_url_extraction():
    """Debug URL extraction by examining actual HTML structure"""
    
    print("🔍 DEBUGGING URL EXTRACTION")
    print("=" * 50)
    
    try:
        # Initialize scraper
        scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=False)
        
        # Setup the WebDriver
        print("🔧 Setting up WebDriver...")
        scraper.setup_driver()
        
        # Get the first page to analyze
        print("📄 Fetching first page for analysis...")
        
        # Navigate to the search page
        search_url = "https://www.magicbricks.com/flats-in-gurgaon-for-sale-pppfs"
        scraper.driver.get(search_url)
        time.sleep(5)  # Wait for page load
        
        # Get page source
        soup = BeautifulSoup(scraper.driver.page_source, 'html.parser')
        
        # Find property cards
        property_cards = scraper._find_property_cards(soup)
        
        print(f"🏠 Found {len(property_cards)} property cards")
        
        if not property_cards:
            print("❌ No property cards found. Let's examine the page structure...")
            
            # Save page source for manual inspection
            with open('debug_page_source.html', 'w', encoding='utf-8') as f:
                f.write(scraper.driver.page_source)
            print("💾 Saved page source to debug_page_source.html")
            
            return
        
        print("\n🔍 ANALYZING FIRST 5 PROPERTY CARDS:")
        print("=" * 50)
        
        for i, card in enumerate(property_cards[:5], 1):
            print(f"\n🏠 PROPERTY CARD {i}:")
            print("-" * 30)
            
            # Extract title for identification
            title = scraper._extract_with_fallback(card, [
                'h2.mb-srp__card--title',
                'h2[class*="title"]',
                'h3[class*="title"]',
                'a[class*="title"]'
            ], 'No title found')
            print(f"📝 Title: {title[:60]}...")
            
            # Try to find all links in the card
            all_links = card.find_all('a', href=True)
            print(f"🔗 Total links found: {len(all_links)}")
            
            if all_links:
                print("\n🔗 ALL LINKS IN CARD:")
                for j, link in enumerate(all_links, 1):
                    href = link.get('href', '')
                    link_text = link.get_text(strip=True)[:50]
                    print(f"   {j}. {href}")
                    print(f"      Text: {link_text}")
                    print(f"      Classes: {link.get('class', [])}")
                    print()
            
            # Test current URL extraction logic
            print("🧪 TESTING CURRENT URL EXTRACTION:")
            url_selectors = [
                'a[href*="/propertydetail/"]',
                'a[href*="/property-details/"]',
                'a[href*="magicbricks.com"]',
                'a[href]'
            ]
            
            for selector in url_selectors:
                try:
                    link = card.select_one(selector)
                    if link and link.get('href'):
                        href = link.get('href')
                        print(f"   ✅ {selector}: {href}")
                        if 'magicbricks.com' in href or href.startswith('/'):
                            print(f"      ✅ Valid URL found: {href}")
                            break
                    else:
                        print(f"   ❌ {selector}: No match")
                except Exception as e:
                    print(f"   💥 {selector}: Error - {str(e)}")
            
            # Test alternative URL patterns
            print("\n🔍 TESTING ALTERNATIVE URL PATTERNS:")
            alternative_selectors = [
                'a[href*="property"]',
                'a[href*="pdpid"]',
                'a[href*="/property/"]',
                'a[href*="/prop/"]',
                'a[href*="detail"]',
                'a[data-url]',
                'a[data-href]'
            ]
            
            for selector in alternative_selectors:
                try:
                    link = card.select_one(selector)
                    if link:
                        href = link.get('href') or link.get('data-url') or link.get('data-href')
                        if href:
                            print(f"   🔍 {selector}: {href}")
                except Exception as e:
                    print(f"   💥 {selector}: Error - {str(e)}")
            
            # Save individual card HTML for inspection
            card_filename = f'debug_card_{i}.html'
            with open(card_filename, 'w', encoding='utf-8') as f:
                f.write(str(card.prettify()))
            print(f"💾 Saved card HTML to {card_filename}")
            
            print("\n" + "="*50)
        
        print("\n💡 RECOMMENDATIONS:")
        print("1. Check the saved HTML files to understand the current structure")
        print("2. Look for new URL patterns in the property cards")
        print("3. Update the URL extraction selectors based on findings")
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        if 'scraper' in locals():
            scraper.close()

if __name__ == "__main__":
    debug_url_extraction()