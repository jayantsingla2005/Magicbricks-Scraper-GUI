#!/usr/bin/env python3
"""
Debug Failed Property Extractions
Analyzes why specific property cards fail to extract data
"""

import sys
import os
from bs4 import BeautifulSoup

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper

def debug_failed_properties():
    """
    Debug specific property cards that fail extraction
    """
    
    print("🔍 DEBUGGING FAILED PROPERTY EXTRACTIONS")
    print("=" * 60)
    
    # Read the saved HTML file
    html_file = "debug_bot_detection.html"
    if not os.path.exists(html_file):
        print(f"❌ HTML file {html_file} not found")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Create scraper instance
    scraper = IntegratedMagicBricksScraper(headless=True)
    
    # Find property cards
    property_cards = scraper._find_property_cards(soup)
    print(f"Found {len(property_cards)} property cards")
    
    # Failed property indices from previous analysis
    failed_indices = [4, 9, 11, 14, 17, 19, 22, 24]  # 1-based indices
    
    print("\n🔍 ANALYZING FAILED PROPERTY CARDS")
    print("-" * 50)
    
    for i, failed_index in enumerate(failed_indices):
        if failed_index <= len(property_cards):
            card = property_cards[failed_index - 1]  # Convert to 0-based
            
            print(f"\n📋 Property {failed_index} Analysis:")
            print("-" * 30)
            
            # Check card structure
            print(f"Card tag: {card.name}")
            print(f"Card classes: {card.get('class', [])}")
            print(f"Card attributes: {dict(card.attrs)}")
            
            # Check for title selectors
            title_selectors = [
                'h2 a',
                '.mb-srp__card--title a',
                '.mb-srp__card__title a',
                'a[title]',
                '.card-title a',
                'h3 a',
                'h4 a'
            ]
            
            print("\nTitle extraction attempts:")
            for selector in title_selectors:
                elements = card.select(selector)
                if elements:
                    title = elements[0].get_text(strip=True)
                    href = elements[0].get('href', '')
                    print(f"  ✅ {selector}: '{title[:50]}...' (URL: {href[:30]}...)")
                else:
                    print(f"  ❌ {selector}: No match")
            
            # Check for price selectors
            price_selectors = [
                '.mb-srp__card__price--amount',
                '.mb-srp__card--price',
                '.price',
                '[class*="price"]',
                '.amount'
            ]
            
            print("\nPrice extraction attempts:")
            for selector in price_selectors:
                elements = card.select(selector)
                if elements:
                    price = elements[0].get_text(strip=True)
                    print(f"  ✅ {selector}: '{price}'")
                else:
                    print(f"  ❌ {selector}: No match")
            
            # Check for area selectors
            area_selectors = [
                '.mb-srp__card__summary--value',
                '.mb-srp__card--carpet-area',
                '.area',
                '[class*="area"]',
                '.carpet-area'
            ]
            
            print("\nArea extraction attempts:")
            for selector in area_selectors:
                elements = card.select(selector)
                if elements:
                    area = elements[0].get_text(strip=True)
                    print(f"  ✅ {selector}: '{area}'")
                else:
                    print(f"  ❌ {selector}: No match")
            
            # Show raw HTML structure (first 500 chars)
            print("\nRaw HTML structure:")
            card_html = str(card)[:500]
            print(f"{card_html}...")
            
            # Try to extract with current method
            print("\nCurrent extraction result:")
            try:
                property_data = scraper.extract_property_data(card, 1, failed_index)
                if property_data:
                    print(f"  Title: {property_data.get('title', 'N/A')}")
                    print(f"  Price: {property_data.get('price', 'N/A')}")
                    print(f"  Area: {property_data.get('area', 'N/A')}")
                    print(f"  URL: {property_data.get('property_url', 'N/A')}")
                else:
                    print("  ❌ No data extracted")
            except Exception as e:
                print(f"  ❌ Exception: {str(e)}")
            
            if i >= 2:  # Limit to first 3 failed properties for readability
                print("\n... (showing first 3 failed properties only)")
                break
    
    print("\n🔍 COMMON PATTERNS IN FAILED CARDS")
    print("-" * 50)
    
    # Analyze common patterns
    failed_cards = [property_cards[i-1] for i in failed_indices if i <= len(property_cards)]
    
    # Check if they have different class patterns
    all_classes = set()
    for card in failed_cards:
        classes = card.get('class', [])
        all_classes.update(classes)
    
    print(f"Classes found in failed cards: {sorted(all_classes)}")
    
    # Check if they're missing key elements
    missing_elements = {
        'links': 0,
        'price_elements': 0,
        'area_elements': 0
    }
    
    for card in failed_cards:
        if not card.select('a'):
            missing_elements['links'] += 1
        if not card.select('[class*="price"]'):
            missing_elements['price_elements'] += 1
        if not card.select('[class*="area"], [class*="sqft"], [class*="carpet"]'):
            missing_elements['area_elements'] += 1
    
    print(f"\nMissing elements in failed cards:")
    for element, count in missing_elements.items():
        print(f"  • {element}: {count}/{len(failed_cards)} cards")
    
    print("\n💡 RECOMMENDATIONS")
    print("-" * 30)
    print("1. Add more fallback selectors for title, price, and area")
    print("2. Implement more flexible text extraction methods")
    print("3. Add debugging logs to identify extraction failures")
    print("4. Consider using more generic selectors as fallbacks")
    print("5. Implement partial data extraction (accept cards with some missing fields)")
    
    print("\n🎉 Debug Analysis Complete!")
    print("=" * 60)

if __name__ == "__main__":
    debug_failed_properties()