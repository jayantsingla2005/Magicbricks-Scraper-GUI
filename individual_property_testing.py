#!/usr/bin/env python3
"""
Individual Property Page Testing
Tests extraction from individual property detail pages
This is the critical Phase 1 task that was overlooked
"""

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
import pandas as pd
import time
from bs4 import BeautifulSoup

def test_individual_property_pages():
    """Test individual property page extraction - the critical missing validation"""
    
    print('🔍 INDIVIDUAL PROPERTY PAGE TESTING...')
    print('=' * 60)
    print('⚠️ This is the critical Phase 1 task that was not properly validated')
    print('=' * 60)
    
    # First, get some property URLs from listing pages
    scraper = IntegratedMagicBricksScraper()
    
    print('📋 Step 1: Getting property URLs from listing pages...')
    result = scraper.scrape_properties_with_incremental(
        city='gurgaon',
        max_pages=1,
        export_formats=[]
    )
    
    # Extract URLs that exist
    property_urls = []
    for prop in scraper.properties:
        url = prop.get('property_url', '').strip()
        if url and url != '' and 'magicbricks.com' in url:
            property_urls.append(url)
    
    print(f'✅ Found {len(property_urls)} valid property URLs from listing page')
    
    if len(property_urls) == 0:
        print('❌ No valid property URLs found - cannot test individual pages')
        scraper.close()
        return
    
    # Test individual property page extraction
    print(f'\n📋 Step 2: Testing individual property page extraction...')
    print(f'🎯 Testing first {min(5, len(property_urls))} individual property pages')
    
    individual_results = []
    
    for i, url in enumerate(property_urls[:5]):
        print(f'\n🏡 TESTING INDIVIDUAL PROPERTY {i+1}:')
        print(f'🔗 URL: {url}')
        
        try:
            # Test individual property extraction
            individual_data = test_single_individual_property(scraper, url)
            individual_data['test_index'] = i + 1
            individual_data['source_url'] = url
            individual_results.append(individual_data)
            
            # Print key findings
            print(f'   📝 Title: {individual_data.get("title", "NOT FOUND")[:60]}...')
            print(f'   💰 Price: {individual_data.get("price", "NOT FOUND")}')
            print(f'   📏 Area: {individual_data.get("area", "NOT FOUND")}')
            print(f'   📝 Description: {"YES" if individual_data.get("description") else "NO"} ({len(str(individual_data.get("description", "")))} chars)')
            print(f'   🏠 Property Type: {individual_data.get("property_type", "NOT FOUND")}')
            print(f'   📍 Locality: {individual_data.get("locality", "NOT FOUND")}')
            print(f'   🏢 Society: {individual_data.get("society", "NOT FOUND")}')
            print(f'   📊 Total Fields: {individual_data.get("total_fields_found", 0)}')
            
        except Exception as e:
            print(f'   ❌ Error testing individual property: {str(e)}')
            individual_results.append({
                'test_index': i + 1,
                'source_url': url,
                'error': str(e),
                'total_fields_found': 0
            })
    
    # Close scraper
    scraper.close()
    
    # Save results
    if individual_results:
        df = pd.DataFrame(individual_results)
        df.to_csv('individual_property_testing_results.csv', index=False)
        print(f'\n💾 Saved {len(individual_results)} individual property tests to individual_property_testing_results.csv')
        
        # Analysis
        print('\n📊 INDIVIDUAL PROPERTY PAGE ANALYSIS:')
        print('=' * 50)
        
        successful_tests = [r for r in individual_results if 'error' not in r]
        failed_tests = [r for r in individual_results if 'error' in r]
        
        print(f'✅ Successful extractions: {len(successful_tests)}/{len(individual_results)}')
        print(f'❌ Failed extractions: {len(failed_tests)}/{len(individual_results)}')
        
        if successful_tests:
            # Field analysis for successful tests
            print('\n📋 FIELD COMPLETENESS ON INDIVIDUAL PAGES:')
            for field in ['title', 'price', 'area', 'description', 'property_type', 'locality', 'society']:
                filled_count = sum(1 for r in successful_tests if r.get(field) and str(r.get(field)).strip())
                completeness = (filled_count / len(successful_tests)) * 100
                status = '✅' if completeness >= 90 else '⚠️' if completeness >= 50 else '❌'
                print(f'   {status} {field}: {completeness:.1f}% ({filled_count}/{len(successful_tests)})')
            
            # Compare with listing page data
            print('\n🔄 COMPARISON: Individual Pages vs Listing Pages:')
            print('   📝 Description on individual pages: Much more detailed content expected')
            print('   📍 Locality on individual pages: Should be available')
            print('   🏢 Society on individual pages: Should be available')
            print('   📊 Additional fields: Amenities, floor plans, etc.')
        
        if failed_tests:
            print('\n❌ FAILED TESTS:')
            for test in failed_tests:
                print(f'   🔗 {test["source_url"]}: {test["error"]}')
    
    return individual_results

def test_single_individual_property(scraper, url):
    """Test extraction from a single individual property page"""
    
    # Navigate to individual property page
    scraper.setup_driver()
    scraper.driver.get(url)
    time.sleep(5)  # Wait for page load
    
    # Get page source
    page_source = scraper.driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Check if page loaded successfully
    title_elem = soup.find('title')
    page_title = title_elem.get_text() if title_elem else ''
    
    if 'access denied' in page_title.lower() or 'error' in page_title.lower():
        raise Exception(f'Page access denied or error: {page_title}')
    
    # Extract data using various approaches
    extracted_data = {}
    
    # Basic extraction
    extracted_data['page_title'] = page_title
    extracted_data['page_length'] = len(page_source)
    
    # Try to extract key fields
    extracted_data['title'] = extract_individual_title(soup)
    extracted_data['price'] = extract_individual_price(soup)
    extracted_data['area'] = extract_individual_area(soup)
    extracted_data['description'] = extract_individual_description(soup)
    extracted_data['property_type'] = extract_individual_property_type(soup)
    extracted_data['locality'] = extract_individual_locality(soup)
    extracted_data['society'] = extract_individual_society(soup)
    extracted_data['amenities'] = extract_individual_amenities(soup)
    extracted_data['floor_details'] = extract_individual_floor_details(soup)
    extracted_data['facing'] = extract_individual_facing(soup)
    extracted_data['parking'] = extract_individual_parking(soup)
    extracted_data['ownership'] = extract_individual_ownership(soup)
    
    # Count total fields found
    extracted_data['total_fields_found'] = sum(1 for v in extracted_data.values() if v and str(v).strip())
    
    # Close driver for this test
    scraper.driver.quit()
    
    return extracted_data

def extract_individual_title(soup):
    """Extract title from individual property page"""
    selectors = ['h1', '.property-title', '*[class*="title"]', 'title']
    for selector in selectors:
        elem = soup.select_one(selector)
        if elem:
            text = elem.get_text(strip=True)
            if text and len(text) > 10:
                return text
    return ''

def extract_individual_price(soup):
    """Extract price from individual property page"""
    selectors = ['*[class*="price"]', '*[class*="cost"]', '*[class*="amount"]']
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and any(char in text for char in ['₹', 'Cr', 'Lac', 'crore', 'lakh']):
                return text
    return ''

def extract_individual_area(soup):
    """Extract area from individual property page"""
    selectors = ['*[class*="area"]', '*[class*="size"]', '*[class*="sqft"]']
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and any(unit in text.lower() for unit in ['sqft', 'sqyrd', 'sq ft', 'sq yrd']):
                return text
    return ''

def extract_individual_description(soup):
    """Extract description from individual property page"""
    # Look for description in various places
    selectors = [
        '*[class*="description"]',
        '*[class*="about"]',
        '*[class*="detail"]',
        '*[class*="overview"]',
        'p'
    ]
    
    descriptions = []
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and len(text) > 100:  # Substantial description
                descriptions.append(text)
    
    # Return the longest description found
    if descriptions:
        return max(descriptions, key=len)[:1000]  # Limit to 1000 chars
    return ''

def extract_individual_property_type(soup):
    """Extract property type from individual property page"""
    selectors = ['*[class*="type"]', '*[class*="category"]']
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and any(ptype in text.lower() for ptype in ['bhk', 'apartment', 'house', 'villa', 'plot']):
                return text
    return ''

def extract_individual_locality(soup):
    """Extract locality from individual property page"""
    selectors = ['*[class*="locality"]', '*[class*="location"]', '*[class*="address"]']
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and len(text) > 5:
                return text
    return ''

def extract_individual_society(soup):
    """Extract society/project name from individual property page"""
    selectors = ['*[class*="society"]', '*[class*="project"]', '*[class*="building"]']
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and len(text) > 3:
                return text
    return ''

def extract_individual_amenities(soup):
    """Extract amenities from individual property page"""
    selectors = ['*[class*="amenity"]', '*[class*="amenities"]', '*[class*="facility"]']
    amenities = []
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text:
                amenities.append(text)
    return ', '.join(amenities[:10]) if amenities else ''  # Limit to first 10

def extract_individual_floor_details(soup):
    """Extract floor details from individual property page"""
    selectors = ['*[class*="floor"]']
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and 'floor' in text.lower():
                return text
    return ''

def extract_individual_facing(soup):
    """Extract facing direction from individual property page"""
    selectors = ['*[class*="facing"]', '*[class*="direction"]']
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and any(direction in text.lower() for direction in ['north', 'south', 'east', 'west']):
                return text
    return ''

def extract_individual_parking(soup):
    """Extract parking details from individual property page"""
    selectors = ['*[class*="parking"]', '*[class*="garage"]']
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and 'parking' in text.lower():
                return text
    return ''

def extract_individual_ownership(soup):
    """Extract ownership details from individual property page"""
    selectors = ['*[class*="ownership"]', '*[class*="possession"]']
    for selector in selectors:
        elems = soup.select(selector)
        for elem in elems:
            text = elem.get_text(strip=True)
            if text and any(own in text.lower() for own in ['freehold', 'leasehold', 'ownership']):
                return text
    return ''

if __name__ == "__main__":
    test_individual_property_pages()
