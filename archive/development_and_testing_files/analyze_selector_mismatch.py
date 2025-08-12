#!/usr/bin/env python3
"""
Analyze why area and link extraction is failing for specific properties
This script will examine the actual HTML structure and test the selectors
"""

import os
import sys
from bs4 import BeautifulSoup
import re

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_selector_mismatch():
    """Analyze why selectors are failing for specific properties"""
    
    print("🔍 ANALYZING SELECTOR MISMATCH")
    print("=" * 50)
    
    # Read the saved HTML file
    html_file = 'debug_bot_detection.html'
    if not os.path.exists(html_file):
        print(f"❌ HTML file {html_file} not found")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find property cards using the same logic as the scraper
    property_cards = soup.select('div.mb-srp__card')
    print(f"📊 Found {len(property_cards)} property cards")
    
    # Failed property indices from previous analysis
    failed_indices = [4, 9, 11, 14, 17, 19, 22, 24]
    
    print("\n🔍 ANALYZING FAILED PROPERTIES:")
    print("-" * 40)
    
    for idx in failed_indices:
        if idx < len(property_cards):
            card = property_cards[idx]
            print(f"\n📋 PROPERTY {idx + 1} ANALYSIS:")
            
            # Test area selectors used by the scraper
            area_selectors = [
                'div.mb-srp__card__summary--value',
                'span[class*="area"]',
                'div[class*="area"]',
                '.mb-srp__card__summary--value',
                '.SRPTuple__area',
                '[data-testid*="area"]',
                '*[class*="sqft"]',
                '*[class*="size"]',
                '*[class*="carpet"]'
            ]
            
            print("   🏠 Area Selector Testing:")
            area_found = False
            for selector in area_selectors:
                try:
                    elem = card.select_one(selector)
                    if elem:
                        text = elem.get_text(strip=True)
                        if text and len(text) > 1:
                            print(f"      ✅ {selector}: '{text}'")
                            area_found = True
                            break
                        else:
                            print(f"      ⚠️  {selector}: Found but empty/invalid text")
                    else:
                        print(f"      ❌ {selector}: Not found")
                except Exception as e:
                    print(f"      ❌ {selector}: Error - {str(e)}")
            
            if not area_found:
                print("      🔍 Manual area search in card text:")
                card_text = card.get_text()
                area_patterns = [
                    r'(\d+[\d,.]*)\s*(?:sqft|sq\.?\s*ft|Sq\.?\s*ft)',
                    r'Super Area[:\s]*(\d+[\d,.]*)\s*(?:sqft|sq\.?\s*ft)',
                    r'Carpet Area[:\s]*(\d+[\d,.]*)\s*(?:sqft|sq\.?\s*ft)',
                    r'Area[:\s]*(\d+[\d,.]*)\s*(?:sqft|sq\.?\s*ft)'
                ]
                
                for pattern in area_patterns:
                    matches = re.findall(pattern, card_text, re.IGNORECASE)
                    if matches:
                        print(f"         ✅ Pattern '{pattern}': {matches}")
                        break
                else:
                    print("         ❌ No area patterns found in text")
                    # Show a snippet of the card text
                    snippet = ' '.join(card_text.split()[:20])
                    print(f"         📝 Card text snippet: {snippet}...")
            
            # Test URL selectors
            print("   🔗 URL Selector Testing:")
            url_selectors = [
                'a[href*="property-detail"]',
                'a[href*="/property/"]',
                'h2 a',
                'h3 a',
                'a[class*="title"]',
                'a'
            ]
            
            url_found = False
            for selector in url_selectors:
                try:
                    elem = card.select_one(selector)
                    if elem and elem.get('href'):
                        href = elem.get('href')
                        if 'property' in href or 'detail' in href:
                            print(f"      ✅ {selector}: '{href[:50]}...'")
                            url_found = True
                            break
                        else:
                            print(f"      ⚠️  {selector}: Found but not property URL: '{href[:30]}...'")
                    else:
                        print(f"      ❌ {selector}: Not found or no href")
                except Exception as e:
                    print(f"      ❌ {selector}: Error - {str(e)}")
            
            if not url_found:
                print("      🔍 All links in this card:")
                all_links = card.find_all('a')
                if all_links:
                    for i, link in enumerate(all_links[:3]):  # Show first 3 links
                        href = link.get('href', 'No href')
                        text = link.get_text(strip=True)[:30]
                        print(f"         Link {i+1}: href='{href[:40]}...', text='{text}...'")
                else:
                    print("         ❌ No links found in this card")
            
            # Check card classes for special types
            card_classes = card.get('class', [])
            print(f"   🏷️  Card classes: {card_classes}")
            
            # Check if this is a special property type
            special_indicators = ['preferred-agent', 'card-luxury', 'premium', 'sponsored']
            special_found = [cls for cls in card_classes if any(indicator in cls for indicator in special_indicators)]
            if special_found:
                print(f"   ⭐ Special property type detected: {special_found}")
            
            print("-" * 40)
    
    print("\n📊 SUMMARY:")
    print("The analysis shows that the scraper's selectors may not be comprehensive enough")
    print("for all property card variations, especially premium/sponsored listings.")
    print("\nRecommendations:")
    print("1. Add more flexible area extraction patterns")
    print("2. Improve URL detection for special property types")
    print("3. Handle premium/sponsored cards differently")
    print("4. Add regex-based fallback extraction")

if __name__ == "__main__":
    analyze_selector_mismatch()