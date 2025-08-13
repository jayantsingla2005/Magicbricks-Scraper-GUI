#!/usr/bin/env python3
"""
Description Research via Working Scraper
Use the working scraper to get HTML and analyze description extraction
"""

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
import time
from bs4 import BeautifulSoup
import json

def description_research_via_scraper():
    """Research description extraction using the working scraper approach"""
    
    print('🔍 DESCRIPTION RESEARCH VIA WORKING SCRAPER')
    print('=' * 60)
    
    # Create scraper instance and run it to get HTML
    scraper = IntegratedMagicBricksScraper()
    
    # Modify the scraper to capture HTML during normal operation
    original_extract_properties = scraper._extract_properties_from_page
    
    captured_html = []
    captured_cards = []
    
    def capture_html_extract_properties(soup, page_num):
        """Modified extraction that captures HTML for analysis"""
        
        # Find property cards
        property_cards = soup.select('.mb-srp__card')
        
        # Capture first 3 cards for analysis
        if page_num == 1 and len(property_cards) > 0:
            for i, card in enumerate(property_cards[:3]):
                captured_cards.append(card)
                captured_html.append(card.prettify())
        
        # Call original method
        return original_extract_properties(soup, page_num)
    
    # Replace the method temporarily
    scraper._extract_properties_from_page = capture_html_extract_properties
    
    print('📋 Running scraper to capture HTML...')
    
    # Run scraper for 1 page
    result = scraper.scrape_properties_with_incremental(
        city='gurgaon',
        max_pages=1,
        export_formats=[]
    )
    
    print(f'✅ Captured {len(captured_cards)} property cards for analysis')
    
    if len(captured_cards) == 0:
        print('❌ No property cards captured')
        scraper.close()
        return
    
    # Now analyze the captured cards
    for i, card in enumerate(captured_cards):
        print(f'\n🏡 ANALYZING CAPTURED PROPERTY CARD {i+1}:')
        print('=' * 50)
        
        # Get basic info
        title_elem = card.select_one('h2, h3, .mb-srp__card__title, *[class*="title"]')
        title = title_elem.get_text(strip=True) if title_elem else 'NO TITLE'
        print(f'📝 Property: {title[:60]}...')
        
        # Analyze all text content
        all_text = card.get_text()
        print(f'📊 Total text length: {len(all_text)} characters')
        
        # Find all paragraphs
        all_paragraphs = card.find_all('p')
        print(f'\n📋 FOUND {len(all_paragraphs)} PARAGRAPH ELEMENTS:')
        
        description_candidates = []
        
        for j, p in enumerate(all_paragraphs):
            text = p.get_text(strip=True)
            classes = p.get('class', [])
            
            print(f'   📝 P{j+1}: "{text[:80]}{"..." if len(text) > 80 else ""}"')
            print(f'       📊 Length: {len(text)} chars')
            print(f'       🏷️ Classes: {classes}')
            
            # Check if this could be a description
            if len(text) > 30:
                # Check for description indicators
                has_property_keywords = any(keyword in text.lower() for keyword in [
                    'bhk', 'apartment', 'flat', 'house', 'property', 'sale', 'resale',
                    'located', 'situated', 'available', 'gurgaon', 'sector', 'ready'
                ])
                
                # Check for non-description indicators
                has_skip_patterns = any(skip in text.lower() for skip in [
                    'contact', 'phone', 'owner:', 'photos', 'updated', 'posted',
                    'premium member', 'get phone', 'call now'
                ])
                
                is_description_candidate = has_property_keywords and not has_skip_patterns
                
                print(f'       🎯 Property Keywords: {"YES" if has_property_keywords else "NO"}')
                print(f'       ❌ Skip Patterns: {"YES" if has_skip_patterns else "NO"}')
                print(f'       ✅ Description Candidate: {"YES" if is_description_candidate else "NO"}')
                
                if is_description_candidate:
                    description_candidates.append({
                        'index': j,
                        'text': text,
                        'classes': classes,
                        'length': len(text)
                    })
            print()
        
        # Test current extraction method
        print('🧪 TESTING CURRENT EXTRACTION METHOD:')
        current_result = scraper._extract_description(card)
        print(f'   📝 Current Result: "{current_result}"')
        print(f'   📊 Length: {len(current_result)} chars')
        print(f'   ✅ Success: {"YES" if current_result else "NO"}')
        
        # Show description candidates
        if description_candidates:
            print(f'\n✅ FOUND {len(description_candidates)} DESCRIPTION CANDIDATES:')
            for candidate in description_candidates:
                print(f'   📝 Candidate {candidate["index"]}: "{candidate["text"][:150]}..."')
                print(f'      📊 Length: {candidate["length"]} chars')
                print(f'      🏷️ Classes: {candidate["classes"]}')
                print()
        else:
            print('\n❌ NO DESCRIPTION CANDIDATES FOUND')
        
        # Look for specific description-related elements
        print('🔍 LOOKING FOR DESCRIPTION-RELATED ELEMENTS:')
        
        # Check for elements with description-related classes
        desc_elements = card.select('*[class*="desc"], *[class*="summary"], *[class*="detail"], *[class*="content"], *[class*="info"]')
        if desc_elements:
            print(f'   ✅ Found {len(desc_elements)} elements with description-related classes:')
            for elem in desc_elements[:5]:  # Show first 5
                text = elem.get_text(strip=True)
                classes = elem.get('class', [])
                print(f'      📝 {elem.name}: "{text[:100]}{"..." if len(text) > 100 else ""}"')
                print(f'         🏷️ Classes: {classes}')
        else:
            print('   ❌ No elements with description-related classes found')
        
        # Check for "Read more" or expandable content
        read_more_elements = card.find_all(text=lambda text: text and any(phrase in text.lower() for phrase in ['read more', 'show more', 'view more', 'see more']))
        if read_more_elements:
            print(f'   📖 Found {len(read_more_elements)} "Read more" type elements:')
            for elem in read_more_elements:
                parent = elem.parent if elem.parent else elem
                print(f'      📝 Context: "{parent.get_text(strip=True)[:100]}..."')
        else:
            print('   📖 No "Read more" type elements found')
        
        print('\n' + '='*50)
    
    # Save the first card HTML for manual inspection
    if captured_html:
        with open('captured_property_card_analysis.html', 'w', encoding='utf-8') as f:
            f.write(f'<!-- CAPTURED PROPERTY CARD HTML ANALYSIS -->\n')
            f.write(f'<!-- Generated: {time.strftime("%Y-%m-%d %H:%M:%S")} -->\n')
            f.write(f'<!-- Source: Working scraper capture -->\n\n')
            f.write(captured_html[0])
        
        print(f'💾 Saved first captured card HTML to: captured_property_card_analysis.html')
    
    # Test improved extraction method
    print('\n🔬 TESTING IMPROVED EXTRACTION METHOD:')
    
    for i, card in enumerate(captured_cards):
        print(f'\n🏡 TESTING IMPROVED EXTRACTION ON CARD {i+1}:')
        
        improved_description = extract_description_improved(card)
        current_description = scraper._extract_description(card)
        
        print(f'   📝 Current Method: "{current_description}"')
        print(f'   🔬 Improved Method: "{improved_description}"')
        print(f'   📊 Improvement: {"YES" if len(improved_description) > len(current_description) else "NO"}')
    
    # Close scraper
    scraper.close()
    
    print('\n🎯 RESEARCH SUMMARY:')
    print('=' * 50)
    print('✅ Successfully captured and analyzed property cards from working scraper')
    print('🔬 Tested current and improved extraction methods')
    print('💾 Saved HTML for manual inspection')
    print('\n📋 Key Findings:')
    print('   - Property cards are accessible via working scraper')
    print('   - Need to analyze captured HTML to understand description structure')
    print('   - Current extraction method may need refinement')

def extract_description_improved(card):
    """Improved description extraction method based on research"""
    
    # Strategy 1: Look for substantial paragraphs with property keywords
    all_paragraphs = card.find_all('p')
    
    for p in all_paragraphs:
        text = p.get_text(strip=True)
        
        if len(text) > 50:  # Substantial text
            # Check for property-related keywords
            has_property_keywords = any(keyword in text.lower() for keyword in [
                'bhk', 'apartment', 'flat', 'house', 'villa', 'property', 'sale', 'resale',
                'located', 'situated', 'available', 'ready', 'possession', 'furnished',
                'sector', 'gurgaon', 'noida', 'mumbai', 'delhi', 'bangalore'
            ])
            
            # Check for non-description patterns
            has_skip_patterns = any(skip in text.lower() for skip in [
                'contact', 'phone', 'owner:', 'photos', 'updated', 'posted',
                'premium member', 'get phone', 'call now', 'newly launched'
            ])
            
            if has_property_keywords and not has_skip_patterns:
                # Clean up the text
                text = text.replace('Read more', '').strip()
                text = text.replace('..', '.').strip()
                return text[:500]  # Limit to 500 characters
    
    # Strategy 2: Look for elements with description-related classes
    desc_elements = card.select('*[class*="desc"], *[class*="summary"], *[class*="detail"], *[class*="content"]')
    for elem in desc_elements:
        text = elem.get_text(strip=True)
        if len(text) > 30:
            text = text.replace('Read more', '').strip()
            return text[:500]
    
    # Strategy 3: Look for the longest meaningful text
    all_text_elements = card.find_all(['p', 'div', 'span'])
    meaningful_texts = []
    
    for elem in all_text_elements:
        text = elem.get_text(strip=True)
        if (len(text) > 40 and 
            not any(skip in text.lower() for skip in ['contact', 'phone', 'owner:', 'photos']) and
            any(keyword in text.lower() for keyword in ['bhk', 'property', 'apartment', 'house'])):
            meaningful_texts.append(text)
    
    if meaningful_texts:
        # Return the longest meaningful text
        longest_text = max(meaningful_texts, key=len)
        return longest_text.replace('Read more', '').strip()[:500]
    
    return ''

if __name__ == "__main__":
    description_research_via_scraper()
