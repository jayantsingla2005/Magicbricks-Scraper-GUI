#!/usr/bin/env python3
"""
Test script to verify updated selectors work with current MagicBricks structure
"""

import sys
import os
from bs4 import BeautifulSoup

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper

def test_selectors_on_saved_html():
    """Test our updated selectors on the saved HTML file"""
    
    print("🧪 Testing Updated Selectors on Saved HTML")
    print("=" * 50)
    
    # Read the saved HTML file
    html_file = "debug_bot_detection.html"
    if not os.path.exists(html_file):
        print(f"❌ HTML file {html_file} not found")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Test the updated selectors
    selectors = [
        '.mb-srp__card',  # Updated: removed div prefix for broader matching
        '.mb-srp__list',  # Updated: actual class name found in HTML
        'li.mb-srp__list__item',  # Keep as fallback
        'div.mb-srp__card',  # Keep as fallback
        'div.SRPTuple__cardWrap',
        'div.SRPTuple__card',
        'div.SRPTuple__tupleWrap',
        'article[class*="SRPTuple"]',
        'div[data-id][data-listingid]',
    ]
    
    print("Testing individual selectors:")
    for selector in selectors:
        cards = soup.select(selector)
        print(f"  {selector:<30} -> {len(cards):>3} elements")
        if len(cards) >= 10:
            print(f"    ✅ Good selector (found {len(cards)} cards)")
            
            # Test extracting some basic data from first few cards
            print("    Testing data extraction from first 3 cards:")
            for i, card in enumerate(cards[:3]):
                # Try to find title
                title_selectors = [
                    'h2.mb-srp__card--title',
                    'h2[class*="title"]',
                    'h3[class*="title"]',
                    'a[class*="title"]',
                    '.mb-srp__card--title',
                    'h1', 'h2', 'h3', 'h4'
                ]
                
                title = "N/A"
                for title_sel in title_selectors:
                    title_elem = card.select_one(title_sel)
                    if title_elem:
                        title = title_elem.get_text(strip=True)[:50] + "..."
                        break
                
                # Try to find price
                price_selectors = [
                    'div.mb-srp__card__price--amount',
                    'span[class*="price"]',
                    'div[class*="price"]',
                    '.mb-srp__card__price--amount'
                ]
                
                price = "N/A"
                for price_sel in price_selectors:
                    price_elem = card.select_one(price_sel)
                    if price_elem:
                        price = price_elem.get_text(strip=True)
                        break
                
                print(f"      Card {i+1}: Title='{title}', Price='{price}'")
            
            break
    
    print("\n" + "=" * 50)
    print("✅ Selector testing completed")

def test_scraper_method():
    """Test the scraper's _find_property_cards method"""
    
    print("\n🧪 Testing Scraper Method")
    print("=" * 50)
    
    # Read the saved HTML file
    html_file = "debug_bot_detection.html"
    if not os.path.exists(html_file):
        print(f"❌ HTML file {html_file} not found")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Create scraper instance (without initializing driver)
    scraper = IntegratedMagicBricksScraper(headless=True)
    
    # Test the _find_property_cards method
    try:
        property_cards = scraper._find_property_cards(soup)
        print(f"✅ Found {len(property_cards)} property cards using scraper method")
        
        if property_cards:
            print("\nTesting data extraction on first card:")
            try:
                # Test extract_property_data method on first card
                first_card = property_cards[0]
                property_data = scraper.extract_property_data(first_card, 1, 1)
                
                if property_data:
                    print(f"  Title: {property_data.get('title', 'N/A')}")
                    print(f"  Price: {property_data.get('price', 'N/A')}")
                    print(f"  Area: {property_data.get('area', 'N/A')}")
                    print(f"  URL: {property_data.get('property_url', 'N/A')}")
                    print("  ✅ Data extraction successful")
                else:
                    print("  ❌ No data extracted")
                    
            except Exception as e:
                print(f"  ❌ Error in data extraction: {str(e)}")
        
    except Exception as e:
        print(f"❌ Error in _find_property_cards: {str(e)}")
    
    print("\n" + "=" * 50)
    print("✅ Scraper method testing completed")

if __name__ == "__main__":
    test_selectors_on_saved_html()
    test_scraper_method()
    print("\n🎉 All tests completed!")