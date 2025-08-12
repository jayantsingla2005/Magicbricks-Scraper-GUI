#!/usr/bin/env python3
"""
Analyze HTML structure to find property card patterns
"""

from bs4 import BeautifulSoup
import re

def analyze_html_structure():
    print("=== HTML Structure Analysis ===")
    
    # Read the HTML file
    try:
        with open('debug_bot_detection.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
    except FileNotFoundError:
        print("ERROR: debug_bot_detection.html not found")
        return
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    print(f"Total HTML length: {len(html_content)} characters")
    print(f"Title: {soup.title.string if soup.title else 'No title'}")
    
    # Look for common property card patterns
    property_patterns = [
        'div[data-testid="srp-tuple"]',
        'div[class*="srp-tuple"]',
        'div[class*="mb-srp"]',
        'div[class*="property"]',
        'div[class*="card"]',
        'div[class*="listing"]',
        'div[class*="item"]'
    ]
    
    print("\n=== Searching for Property Card Patterns ===")
    for pattern in property_patterns:
        elements = soup.select(pattern)
        print(f"Pattern '{pattern}': {len(elements)} elements found")
        
        if elements:
            # Show first element's classes and attributes
            first_elem = elements[0]
            print(f"  First element classes: {first_elem.get('class', [])}")
            print(f"  First element attributes: {list(first_elem.attrs.keys())}")
            print(f"  First element text preview: {first_elem.get_text(strip=True)[:100]}...")
    
    # Look for any divs with specific attributes that might be property cards
    print("\n=== All divs with data-testid ===")
    testid_divs = soup.find_all('div', attrs={'data-testid': True})
    for div in testid_divs[:10]:  # Show first 10
        print(f"  data-testid='{div.get('data-testid')}' - classes: {div.get('class', [])}")
    
    # Look for links that might contain property URLs
    print("\n=== Property URL Patterns ===")
    url_patterns = [
        'propertydetail',
        'property-details',
        'property-for-sale',
        'magicbricks.com'
    ]
    
    all_links = soup.find_all('a', href=True)
    print(f"Total links found: {len(all_links)}")
    
    for pattern in url_patterns:
        matching_links = [link for link in all_links if pattern in link.get('href', '')]
        print(f"Links containing '{pattern}': {len(matching_links)}")
        
        if matching_links:
            # Show first few examples
            for i, link in enumerate(matching_links[:3]):
                href = link.get('href', '')
                text = link.get_text(strip=True)[:50]
                print(f"  {i+1}. {href[:80]}... (text: '{text}')")
    
    # Look for common class patterns
    print("\n=== Common Class Patterns ===")
    all_elements = soup.find_all(True)  # Find all elements
    class_counts = {}
    
    for elem in all_elements:
        classes = elem.get('class', [])
        for cls in classes:
            if any(keyword in cls.lower() for keyword in ['srp', 'property', 'card', 'listing', 'item']):
                class_counts[cls] = class_counts.get(cls, 0) + 1
    
    # Show most common relevant classes
    sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
    for cls, count in sorted_classes[:10]:
        print(f"  '{cls}': {count} occurrences")
    
    # Check if page is fully loaded or if it's a loading state
    print("\n=== Page Loading State ===")
    loading_indicators = soup.find_all(text=re.compile(r'loading|Loading|LOADING', re.I))
    print(f"Loading indicators found: {len(loading_indicators)}")
    
    # Check for JavaScript-rendered content indicators
    script_tags = soup.find_all('script')
    print(f"Script tags found: {len(script_tags)}")
    
    # Look for React/dynamic content indicators
    react_indicators = soup.find_all(attrs={'data-reactroot': True})
    print(f"React root elements: {len(react_indicators)}")
    
    # Check for any error messages
    error_patterns = ['error', 'Error', 'ERROR', 'not found', 'Not Found', 'access denied', 'Access Denied']
    for pattern in error_patterns:
        if pattern.lower() in html_content.lower():
            print(f"  Found potential error indicator: '{pattern}'")
    
    print("\n=== Analysis Complete ===")

if __name__ == "__main__":
    analyze_html_structure()