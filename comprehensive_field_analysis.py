#!/usr/bin/env python3
"""
Comprehensive Field Analysis for MagicBricks Scraper
Deep analysis of ALL fields across ALL property types
"""

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
import pandas as pd
import time
from bs4 import BeautifulSoup

def comprehensive_field_analysis():
    """Comprehensive analysis of all fields across all property types"""
    
    print('🔍 COMPREHENSIVE FIELD ANALYSIS STARTING...')
    print('=' * 60)
    
    # Create scraper instance
    scraper = IntegratedMagicBricksScraper()
    
    # Test different property type searches
    test_searches = [
        {
            'name': 'Apartments/Flats',
            'url': 'https://www.magicbricks.com/flats-in-gurgaon-for-sale-pppfs',
            'expected_types': ['apartment', 'flat', 'bhk']
        },
        {
            'name': 'Houses/Villas', 
            'url': 'https://www.magicbricks.com/independent-house-for-sale-in-gurgaon-pppfs',
            'expected_types': ['house', 'villa', 'independent']
        },
        {
            'name': 'Builder Floors',
            'url': 'https://www.magicbricks.com/builder-floor-for-sale-in-gurgaon-pppfs', 
            'expected_types': ['builder floor', 'floor']
        },
        {
            'name': 'Plots/Land',
            'url': 'https://www.magicbricks.com/residential-plots-land-for-sale-in-gurgaon-pppfs',
            'expected_types': ['plot', 'land', 'residential']
        }
    ]
    
    scraper.setup_driver()
    
    all_results = []
    
    for search in test_searches:
        print(f'\n🏠 TESTING: {search["name"]}')
        print(f'🔗 URL: {search["url"]}')
        print('-' * 50)
        
        try:
            # Navigate to the specific property type page
            scraper.driver.get(search['url'])
            time.sleep(5)  # Wait for page load
            
            # Get page source and parse
            page_source = scraper.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find property cards
            property_cards = soup.select('.mb-srp__card')
            print(f'📊 Found {len(property_cards)} property cards')
            
            if len(property_cards) == 0:
                print('❌ No property cards found - checking page content...')
                title = soup.find('title')
                print(f'📄 Page title: {title.get_text() if title else "No title"}')
                continue
            
            # Analyze first 3 properties in detail
            for i, card in enumerate(property_cards[:3]):
                print(f'\n🏡 PROPERTY {i+1} ANALYSIS:')
                
                # Extract all possible fields
                analysis = analyze_property_card(card, scraper)
                analysis['property_type_search'] = search['name']
                analysis['property_index'] = i + 1
                
                all_results.append(analysis)
                
                # Print key findings
                print(f'   📝 Title: {analysis.get("title", "NOT FOUND")[:60]}...')
                print(f'   💰 Price: {analysis.get("price", "NOT FOUND")}')
                print(f'   📏 Area: {analysis.get("area", "NOT FOUND")}')
                print(f'   👤 Posted By: {analysis.get("posted_by", "NOT FOUND")}')
                print(f'   📸 Photos: {analysis.get("photo_count", "NOT FOUND")}')
                print(f'   📝 Description: {analysis.get("description", "NOT FOUND")[:100]}...')
                print(f'   🔗 URL: {analysis.get("property_url", "NOT FOUND")}')
                
        except Exception as e:
            print(f'❌ Error testing {search["name"]}: {str(e)}')
    
    # Close driver
    scraper.driver.quit()
    
    # Save comprehensive results
    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv('comprehensive_field_analysis.csv', index=False)
        print(f'\n💾 Saved {len(all_results)} property analyses to comprehensive_field_analysis.csv')
        
        # Field completeness analysis
        print('\n📊 FIELD COMPLETENESS ANALYSIS:')
        print('=' * 50)
        
        for column in df.columns:
            if column not in ['property_type_search', 'property_index']:
                filled_count = df[column].notna().sum()
                non_empty_count = df[column].astype(str).str.strip().ne('').sum()
                completeness = (non_empty_count / len(df)) * 100
                print(f'   📊 {column}: {completeness:.1f}% ({non_empty_count}/{len(df)})')
    
    return all_results

def analyze_property_card(card, scraper):
    """Detailed analysis of a single property card"""
    
    analysis = {}
    
    # Basic fields using existing scraper methods
    try:
        analysis['title'] = scraper._extract_title(card)
        analysis['price'] = scraper._extract_price(card)
        analysis['area'] = scraper._extract_area(card)
        analysis['property_url'] = scraper._extract_property_url(card)
        analysis['photo_count'] = scraper._extract_photo_count(card)
        analysis['owner_name'] = scraper._extract_owner_name(card)
        analysis['contact_options'] = scraper._extract_contact_options(card)
        analysis['description'] = scraper._extract_description(card)
    except Exception as e:
        print(f'   ⚠️ Error in basic extraction: {str(e)}')
    
    # Deep analysis for "Posted By" field
    try:
        analysis['posted_by'] = extract_posted_by_field(card)
    except Exception as e:
        analysis['posted_by'] = f'ERROR: {str(e)}'
    
    # Deep analysis for description field with multiple approaches
    try:
        analysis['description_deep'] = deep_description_analysis(card)
    except Exception as e:
        analysis['description_deep'] = f'ERROR: {str(e)}'
    
    # Property type detection
    try:
        analysis['detected_property_type'] = detect_property_type(card)
    except Exception as e:
        analysis['detected_property_type'] = f'ERROR: {str(e)}'
    
    # All paragraph texts for debugging
    try:
        all_paragraphs = card.find_all('p')
        analysis['all_paragraph_texts'] = ' | '.join([p.get_text(strip=True) for p in all_paragraphs if p.get_text(strip=True)])
    except Exception as e:
        analysis['all_paragraph_texts'] = f'ERROR: {str(e)}'
    
    return analysis

def extract_posted_by_field(card):
    """Extract 'Posted By' information (Builder/Owner/Dealer/Premium)"""
    
    # Look for posted by indicators
    posted_by_selectors = [
        '*[class*="owner"]',
        '*[class*="builder"]', 
        '*[class*="dealer"]',
        '*[class*="agent"]',
        '*[class*="premium"]',
        '*[class*="posted"]',
        '*[class*="member"]'
    ]
    
    for selector in posted_by_selectors:
        elements = card.select(selector)
        for elem in elements:
            text = elem.get_text(strip=True)
            if text and any(keyword in text.lower() for keyword in ['owner', 'builder', 'dealer', 'agent', 'premium', 'member']):
                return text
    
    # Look in all text for posted by patterns
    all_text = card.get_text()
    posted_by_patterns = ['owner:', 'builder:', 'dealer:', 'agent:', 'posted by', 'premium member']
    
    for pattern in posted_by_patterns:
        if pattern in all_text.lower():
            # Extract surrounding text
            start_idx = all_text.lower().find(pattern)
            surrounding_text = all_text[max(0, start_idx-10):start_idx+50]
            return surrounding_text.strip()
    
    return ''

def deep_description_analysis(card):
    """Deep analysis of description field with multiple extraction approaches"""
    
    description_approaches = []
    
    # Approach 1: All paragraphs
    paragraphs = card.find_all('p')
    for i, p in enumerate(paragraphs):
        text = p.get_text(strip=True)
        if len(text) > 50:
            description_approaches.append(f'P{i+1}: {text[:200]}...')
    
    # Approach 2: Specific selectors
    desc_selectors = [
        '*[class*="description"]',
        '*[class*="summary"]', 
        '*[class*="detail"]',
        '*[class*="content"]',
        '*[class*="info"]'
    ]
    
    for selector in desc_selectors:
        elements = card.select(selector)
        for elem in elements:
            text = elem.get_text(strip=True)
            if len(text) > 30:
                description_approaches.append(f'{selector}: {text[:200]}...')
    
    # Approach 3: Look for "Read more" indicators
    read_more_elements = card.find_all(text=lambda text: text and 'read more' in text.lower())
    for elem in read_more_elements:
        parent = elem.parent if elem.parent else elem
        text = parent.get_text(strip=True)
        if len(text) > 50:
            description_approaches.append(f'ReadMore: {text[:200]}...')
    
    return ' | '.join(description_approaches) if description_approaches else 'NO_DESCRIPTION_FOUND'

def detect_property_type(card):
    """Detect the actual property type from the card content"""
    
    all_text = card.get_text().lower()
    
    property_types = {
        'apartment': ['apartment', 'flat', 'bhk'],
        'house': ['house', 'villa', 'independent house'],
        'builder_floor': ['builder floor', 'floor'],
        'plot': ['plot', 'land', 'residential plot'],
        'commercial': ['commercial', 'office', 'shop']
    }
    
    detected_types = []
    for prop_type, keywords in property_types.items():
        if any(keyword in all_text for keyword in keywords):
            detected_types.append(prop_type)
    
    return ', '.join(detected_types) if detected_types else 'unknown'

if __name__ == "__main__":
    comprehensive_field_analysis()
