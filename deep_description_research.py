#!/usr/bin/env python3
"""
Deep Description Field Research
Comprehensive investigation into why description field is 0% complete
Tests multiple extraction approaches and analyzes HTML structure
"""

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
import time
from bs4 import BeautifulSoup
import json

def deep_description_research():
    """Comprehensive research into description field extraction"""
    
    print('🔍 DEEP DESCRIPTION FIELD RESEARCH')
    print('=' * 60)
    print('🎯 Goal: Understand why description field is 0% complete across ALL properties')
    print('=' * 60)
    
    # Create scraper instance
    scraper = IntegratedMagicBricksScraper()
    scraper.setup_driver()
    
    # Navigate to listing page
    url = 'https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs'
    print(f'🔗 Navigating to: {url}')
    scraper.driver.get(url)
    time.sleep(5)
    
    # Get page source
    page_source = scraper.driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Find property cards
    property_cards = soup.select('.mb-srp__card')
    print(f'📊 Found {len(property_cards)} property cards')
    
    if len(property_cards) == 0:
        print('❌ No property cards found')
        scraper.driver.quit()
        return
    
    # Analyze first 3 property cards in extreme detail
    for i, card in enumerate(property_cards[:3]):
        print(f'\n🏡 DETAILED ANALYSIS OF PROPERTY CARD {i+1}:')
        print('=' * 50)
        
        # 1. Extract basic info for context
        title_elem = card.select_one('h2, h3, .mb-srp__card__title, *[class*="title"]')
        title = title_elem.get_text(strip=True) if title_elem else 'NO TITLE'
        print(f'📝 Property: {title[:60]}...')
        
        # 2. Find ALL paragraph elements
        all_paragraphs = card.find_all('p')
        print(f'\n📋 FOUND {len(all_paragraphs)} PARAGRAPH ELEMENTS:')
        
        for j, p in enumerate(all_paragraphs):
            text = p.get_text(strip=True)
            classes = p.get('class', [])
            parent_classes = p.parent.get('class', []) if p.parent else []
            
            print(f'   📝 P{j+1}: "{text[:100]}{"..." if len(text) > 100 else ""}"')
            print(f'       📊 Length: {len(text)} chars')
            print(f'       🏷️ Classes: {classes}')
            print(f'       👆 Parent Classes: {parent_classes}')
            print(f'       🔍 Potential Description: {"YES" if len(text) > 50 and not any(skip in text.lower() for skip in ["contact", "phone", "owner:", "photos"]) else "NO"}')
            print()
        
        # 3. Find ALL div elements that might contain descriptions
        description_divs = card.find_all('div')
        potential_descriptions = []
        
        print(f'📋 ANALYZING {len(description_divs)} DIV ELEMENTS FOR DESCRIPTIONS:')
        for j, div in enumerate(description_divs):
            text = div.get_text(strip=True)
            classes = div.get('class', [])
            
            # Check if this div might contain description
            if (len(text) > 50 and 
                not any(skip in text.lower() for skip in ["contact", "phone", "owner:", "photos", "updated", "posted"]) and
                any(keyword in text.lower() for keyword in ["bhk", "apartment", "flat", "house", "property", "sale", "located", "situated", "available"])):
                
                potential_descriptions.append({
                    'index': j,
                    'text': text,
                    'classes': classes,
                    'length': len(text)
                })
        
        if potential_descriptions:
            print(f'   ✅ FOUND {len(potential_descriptions)} POTENTIAL DESCRIPTIONS:')
            for desc in potential_descriptions:
                print(f'      📝 DIV{desc["index"]}: "{desc["text"][:150]}..."')
                print(f'         📊 Length: {desc["length"]} chars')
                print(f'         🏷️ Classes: {desc["classes"]}')
                print()
        else:
            print('   ❌ NO POTENTIAL DESCRIPTIONS FOUND IN DIVS')
        
        # 4. Check for hidden or dynamically loaded content
        print('🔍 CHECKING FOR HIDDEN/DYNAMIC CONTENT:')
        
        # Look for "Read more" links or buttons
        read_more_elements = card.find_all(text=lambda text: text and 'read more' in text.lower())
        if read_more_elements:
            print(f'   📖 Found {len(read_more_elements)} "Read more" indicators')
            for elem in read_more_elements:
                parent = elem.parent if elem.parent else elem
                print(f'      📝 Context: "{parent.get_text(strip=True)[:100]}..."')
        else:
            print('   📖 No "Read more" indicators found')
        
        # Look for collapsed/expandable content
        expandable_elements = card.select('*[class*="expand"], *[class*="collapse"], *[class*="more"], *[class*="less"]')
        if expandable_elements:
            print(f'   📂 Found {len(expandable_elements)} expandable elements')
            for elem in expandable_elements:
                print(f'      🏷️ Classes: {elem.get("class", [])}')
                print(f'      📝 Text: "{elem.get_text(strip=True)[:100]}..."')
        else:
            print('   📂 No expandable elements found')
        
        # 5. Test current scraper extraction method
        print('🧪 TESTING CURRENT SCRAPER EXTRACTION:')
        extracted_description = scraper._extract_description(card)
        print(f'   📝 Current Method Result: "{extracted_description}"')
        print(f'   📊 Length: {len(extracted_description)} chars')
        print(f'   ✅ Success: {"YES" if extracted_description else "NO"}')
        
        # 6. Try alternative extraction approaches
        print('🔬 TESTING ALTERNATIVE EXTRACTION APPROACHES:')
        
        # Approach A: All text content
        all_text = card.get_text()
        sentences = [s.strip() for s in all_text.split('.') if len(s.strip()) > 50]
        if sentences:
            longest_sentence = max(sentences, key=len)
            print(f'   📝 Approach A (Longest Sentence): "{longest_sentence[:150]}..."')
        else:
            print('   📝 Approach A: No substantial sentences found')
        
        # Approach B: Look for specific description patterns
        description_patterns = ['bhk', 'apartment', 'flat', 'house', 'villa', 'property', 'sale', 'resale']
        pattern_matches = []
        for pattern in description_patterns:
            if pattern in all_text.lower():
                # Extract context around the pattern
                start_idx = all_text.lower().find(pattern)
                context = all_text[max(0, start_idx-50):start_idx+200]
                if len(context.strip()) > 50:
                    pattern_matches.append(context.strip())
        
        if pattern_matches:
            print(f'   📝 Approach B (Pattern Matching): Found {len(pattern_matches)} matches')
            print(f'      Best match: "{pattern_matches[0][:150]}..."')
        else:
            print('   📝 Approach B: No pattern matches found')
        
        print('\n' + '='*50)
    
    # 7. Save detailed HTML for manual inspection
    print('\n💾 SAVING DETAILED HTML FOR MANUAL INSPECTION:')
    
    first_card = property_cards[0]
    with open('property_card_html_analysis.html', 'w', encoding='utf-8') as f:
        f.write(f'<!-- PROPERTY CARD HTML ANALYSIS -->\n')
        f.write(f'<!-- Generated: {time.strftime("%Y-%m-%d %H:%M:%S")} -->\n')
        f.write(f'<!-- Purpose: Manual inspection of property card structure for description extraction -->\n\n')
        f.write(first_card.prettify())
    
    print('   ✅ Saved first property card HTML to: property_card_html_analysis.html')
    
    # 8. Test with JavaScript execution (in case descriptions are loaded dynamically)
    print('\n🔬 TESTING JAVASCRIPT-LOADED CONTENT:')
    
    try:
        # Execute JavaScript to check for dynamic content
        js_result = scraper.driver.execute_script("""
            // Find the first property card
            const firstCard = document.querySelector('.mb-srp__card');
            if (!firstCard) return {error: 'No property card found'};
            
            // Look for any hidden or dynamic content
            const allElements = firstCard.querySelectorAll('*');
            let hiddenContent = [];
            let dynamicContent = [];
            
            allElements.forEach(elem => {
                const style = window.getComputedStyle(elem);
                const text = elem.textContent?.trim();
                
                // Check for hidden content
                if (style.display === 'none' || style.visibility === 'hidden') {
                    if (text && text.length > 50) {
                        hiddenContent.push({
                            tag: elem.tagName,
                            text: text.substring(0, 200),
                            classes: elem.className
                        });
                    }
                }
                
                // Check for content that might be loaded dynamically
                if (elem.hasAttribute('data-description') || 
                    elem.hasAttribute('data-content') ||
                    elem.className.includes('description') ||
                    elem.className.includes('summary')) {
                    dynamicContent.push({
                        tag: elem.tagName,
                        text: text ? text.substring(0, 200) : '',
                        classes: elem.className,
                        attributes: Array.from(elem.attributes).map(attr => `${attr.name}="${attr.value}"`).join(' ')
                    });
                }
            });
            
            return {
                hiddenContent: hiddenContent,
                dynamicContent: dynamicContent,
                totalElements: allElements.length
            };
        """)
        
        print(f'   📊 JavaScript Analysis Results:')
        print(f'      🔍 Total elements analyzed: {js_result.get("totalElements", 0)}')
        print(f'      👻 Hidden content elements: {len(js_result.get("hiddenContent", []))}')
        print(f'      🔄 Dynamic content elements: {len(js_result.get("dynamicContent", []))}')
        
        if js_result.get("hiddenContent"):
            print(f'      👻 Hidden Content Found:')
            for hidden in js_result["hiddenContent"][:3]:  # Show first 3
                print(f'         📝 {hidden["tag"]}: "{hidden["text"][:100]}..."')
        
        if js_result.get("dynamicContent"):
            print(f'      🔄 Dynamic Content Found:')
            for dynamic in js_result["dynamicContent"][:3]:  # Show first 3
                print(f'         📝 {dynamic["tag"]}: "{dynamic["text"][:100]}..."')
                print(f'         🏷️ Classes: {dynamic["classes"]}')
        
    except Exception as e:
        print(f'   ❌ JavaScript analysis failed: {str(e)}')
    
    # Close driver
    scraper.driver.quit()
    
    print('\n🎯 RESEARCH SUMMARY:')
    print('=' * 50)
    print('✅ Completed comprehensive description field research')
    print('📊 Analyzed multiple property cards in extreme detail')
    print('🔬 Tested multiple extraction approaches')
    print('💾 Saved HTML for manual inspection')
    print('🔄 Checked for dynamic/hidden content')
    print('\n📋 Next Steps:')
    print('   1. Review property_card_html_analysis.html manually')
    print('   2. Implement improved extraction based on findings')
    print('   3. Test new extraction method across multiple properties')

if __name__ == "__main__":
    deep_description_research()
