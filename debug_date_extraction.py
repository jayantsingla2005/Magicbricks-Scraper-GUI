#!/usr/bin/env python3
"""
Debug Date Extraction
Investigate why date extraction is not working properly
"""

import requests
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import random


def debug_date_extraction():
    """Debug the date extraction process"""
    
    print("🔍 DEBUGGING DATE EXTRACTION")
    print("="*50)
    
    # Test URL with chronological sorting
    test_url = "https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs?sort=date_desc"
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    try:
        headers = {'User-Agent': random.choice(user_agents)}
        response = requests.get(test_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ HTTP Error: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        property_cards = soup.find_all('div', class_='mb-srp__card')
        
        print(f"📊 Found {len(property_cards)} property cards")
        
        if not property_cards:
            print("❌ No property cards found!")
            return
        
        # Analyze first 5 properties
        for i, card in enumerate(property_cards[:5]):
            print(f"\n🏠 PROPERTY {i+1}:")
            print("-" * 30)
            
            # Get full text
            full_text = card.get_text()
            print(f"📝 Full text length: {len(full_text)} characters")
            
            # Look for date patterns
            date_patterns = [
                (r'Posted:?\s*([^<\n]+)', 'posted_pattern'),
                (r'(\d+)\s+hours?\s+ago', 'hours_ago'),
                (r'(\d+)\s+days?\s+ago', 'days_ago'),
                (r'(\d+)\s+weeks?\s+ago', 'weeks_ago'),
                (r'(\d+)\s+months?\s+ago', 'months_ago'),
                (r'(today)', 'today'),
                (r'(yesterday)', 'yesterday'),
                (r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', 'absolute_date')
            ]
            
            found_dates = []
            for pattern, pattern_type in date_patterns:
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                if matches:
                    found_dates.append((pattern_type, matches))
                    print(f"   ✅ {pattern_type}: {matches}")
            
            if not found_dates:
                print("   ❌ No date patterns found!")
                
                # Show a sample of the text to understand structure
                print(f"   📄 Text sample (first 200 chars):")
                print(f"   {full_text[:200]}...")
                
                # Look for any time-related words
                time_words = ['posted', 'updated', 'listed', 'ago', 'today', 'yesterday', 'hours', 'days', 'weeks', 'months']
                found_time_words = []
                for word in time_words:
                    if word.lower() in full_text.lower():
                        found_time_words.append(word)
                
                if found_time_words:
                    print(f"   🔍 Found time-related words: {found_time_words}")
                else:
                    print("   ❌ No time-related words found!")
            
            # Check specific elements that might contain dates
            date_elements = [
                card.find('span', class_='mb-srp__card__summary--value'),
                card.find('div', class_='mb-srp__card__ads--tag'),
                card.find('span', class_='mb-srp__card__price--amount'),
                card.find('div', class_='mb-srp__card__summary')
            ]
            
            for j, element in enumerate(date_elements):
                if element:
                    element_text = element.get_text(strip=True)
                    if element_text:
                        print(f"   📍 Element {j}: {element_text[:100]}")
        
        print(f"\n🔍 OVERALL ANALYSIS:")
        print("="*50)
        
        # Check if the page structure is different than expected
        all_text = soup.get_text()
        
        # Look for any date-like patterns in the entire page
        all_date_patterns = re.findall(r'\b\d+\s+(hours?|days?|weeks?|months?)\s+ago\b', all_text, re.IGNORECASE)
        today_patterns = re.findall(r'\btoday\b', all_text, re.IGNORECASE)
        posted_patterns = re.findall(r'posted[:\s]*([^<\n]{1,50})', all_text, re.IGNORECASE)
        
        print(f"📊 Date patterns found on entire page:")
        print(f"   - Time ago patterns: {len(all_date_patterns)} ({all_date_patterns[:5]})")
        print(f"   - 'Today' mentions: {len(today_patterns)}")
        print(f"   - 'Posted' patterns: {len(posted_patterns)} ({posted_patterns[:3]})")
        
        # Check if we're getting the right page
        page_title = soup.find('title')
        if page_title:
            print(f"📄 Page title: {page_title.get_text()}")
        
        # Check for any sorting indicators
        sort_indicators = soup.find_all(text=re.compile(r'sort|recent|latest|date', re.IGNORECASE))
        if sort_indicators:
            print(f"🔄 Sort indicators found: {len(sort_indicators)}")
            for indicator in sort_indicators[:3]:
                print(f"   - {indicator.strip()}")
        
    except Exception as e:
        print(f"❌ Debug failed: {str(e)}")


if __name__ == "__main__":
    debug_date_extraction()
