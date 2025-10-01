#!/usr/bin/env python3
"""
Simple Description Test
Direct test of description extraction from scraped data
"""

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
import pandas as pd

def simple_description_test():
    """Simple test to understand description extraction issue"""
    
    print('🔍 SIMPLE DESCRIPTION TEST')
    print('=' * 40)
    
    # Create scraper and get some properties
    scraper = IntegratedMagicBricksScraper()
    
    print('📋 Scraping 1 page to test description extraction...')
    result = scraper.scrape_properties_with_incremental(
        city='gurgaon',
        max_pages=1,
        export_formats=[]
    )
    
    if not scraper.properties:
        print('❌ No properties scraped')
        scraper.close()
        return
    
    print(f'✅ Scraped {len(scraper.properties)} properties')
    
    # Test description extraction on first 3 properties
    for i, prop in enumerate(scraper.properties[:3]):
        print(f'\n🏡 PROPERTY {i+1} DESCRIPTION TEST:')
        print('-' * 40)
        
        title = prop.get('title', 'NO TITLE')
        description = prop.get('description', '')
        
        print(f'📝 Title: {title[:60]}...')
        print(f'📝 Current Description: "{description}"')
        print(f'📊 Description Length: {len(description)} chars')
        print(f'✅ Has Description: {"YES" if description else "NO"}')
        
        # Check if there's any text that could be a description
        # Look at all the fields to see if description is hiding somewhere else
        print('\n🔍 Checking all fields for potential descriptions:')
        for key, value in prop.items():
            if isinstance(value, str) and len(value) > 50:
                # Check if this could be a description
                value_lower = value.lower()
                if any(keyword in value_lower for keyword in ['bhk', 'apartment', 'flat', 'house', 'property', 'located', 'situated']):
                    print(f'   🎯 Potential description in "{key}": "{value[:100]}..."')
    
    # Test the current extraction method directly
    print(f'\n🧪 TESTING CURRENT EXTRACTION METHOD:')
    
    # We need to get the HTML to test extraction
    # Let's run the scraper again but capture the HTML
    scraper.close()
    
    # Create a new scraper instance
    scraper = IntegratedMagicBricksScraper()
    scraper.setup_driver()
    
    # Navigate to the page
    url = 'https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs'
    scraper.driver.get(url)
    
    import time
    time.sleep(5)
    
    # Get page source
    from bs4 import BeautifulSoup
    page_source = scraper.driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find property cards
    property_cards = soup.select('.mb-srp__card')
    print(f'📊 Found {len(property_cards)} property cards in HTML')
    
    if len(property_cards) > 0:
        # Test description extraction on first card
        first_card = property_cards[0]
        
        print(f'\n🔬 TESTING DESCRIPTION EXTRACTION ON FIRST CARD:')
        
        # Get all text from the card
        all_text = first_card.get_text()
        print(f'📊 Total card text length: {len(all_text)} chars')
        
        # Find all paragraphs
        paragraphs = first_card.find_all('p')
        print(f'📋 Found {len(paragraphs)} paragraph elements')
        
        for i, p in enumerate(paragraphs):
            text = p.get_text(strip=True)
            if len(text) > 20:  # Show substantial paragraphs
                print(f'   📝 P{i+1}: "{text[:80]}{"..." if len(text) > 80 else ""}"')
                print(f'       📊 Length: {len(text)} chars')
                
                # Test if this would be selected by current method
                current_result = scraper._extract_description(first_card)
                print(f'   🧪 Current method result: "{current_result}"')
                break
        
        # Test improved extraction
        print(f'\n🔬 TESTING IMPROVED EXTRACTION:')
        improved_result = test_improved_description_extraction(first_card)
        print(f'   🎯 Improved result: "{improved_result}"')
        
    else:
        print('❌ No property cards found in HTML')
    
    scraper.close()

def test_improved_description_extraction(card):
    """Test improved description extraction"""
    
    # Get all text elements
    all_elements = card.find_all(['p', 'div', 'span'])
    
    candidates = []
    
    for elem in all_elements:
        text = elem.get_text(strip=True)
        
        if len(text) > 30:  # Substantial text
            # Check for property keywords
            has_keywords = any(keyword in text.lower() for keyword in [
                'bhk', 'apartment', 'flat', 'house', 'villa', 'property', 
                'sale', 'resale', 'located', 'situated', 'available',
                'ready', 'possession', 'furnished', 'sector'
            ])
            
            # Check for skip patterns
            has_skip = any(skip in text.lower() for skip in [
                'contact', 'phone', 'owner:', 'photos', 'updated', 'posted',
                'premium member', 'get phone', 'call now'
            ])
            
            if has_keywords and not has_skip:
                candidates.append({
                    'text': text,
                    'length': len(text),
                    'element': elem.name,
                    'classes': elem.get('class', [])
                })
    
    if candidates:
        # Return the longest candidate
        best_candidate = max(candidates, key=lambda x: x['length'])
        return best_candidate['text'][:500]  # Limit to 500 chars
    
    return ''

if __name__ == "__main__":
    simple_description_test()
