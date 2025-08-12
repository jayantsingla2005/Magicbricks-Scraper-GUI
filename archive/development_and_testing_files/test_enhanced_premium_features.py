#!/usr/bin/env python3
"""
Test Enhanced Premium Property Features
Verifies the integration of premium property detection and enhanced extraction methods.
"""

import sys
import os
from datetime import datetime
from bs4 import BeautifulSoup

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper

def test_premium_property_detection():
    """Test premium property detection functionality"""
    print("\n🔍 Testing Premium Property Detection")
    print("-" * 50)
    
    # Initialize scraper
    scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=False)
    
    # Test HTML samples for premium properties
    premium_html_samples = [
        '<div class="mb-srp__card mb-srp__card--preferred-agent"><h2>Luxury Apartment</h2></div>',
        '<div class="mb-srp__card mb-srp__card--luxury"><h2>Premium Villa</h2></div>',
        '<div class="mb-srp__card mb-srp__card--premium"><h2>High-end Flat</h2></div>',
        '<div class="mb-srp__card mb-srp__card--sponsored"><h2>Sponsored Property</h2></div>'
    ]
    
    standard_html_samples = [
        '<div class="mb-srp__card"><h2>Regular Apartment</h2></div>',
        '<div class="property-card"><h2>Standard Villa</h2></div>'
    ]
    
    premium_detected = 0
    standard_detected = 0
    
    # Test premium properties
    for i, html in enumerate(premium_html_samples):
        soup = BeautifulSoup(html, 'html.parser')
        card = soup.find('div')
        
        premium_info = scraper.detect_premium_property_type(card)
        
        if premium_info['is_premium']:
            premium_detected += 1
            print(f"✅ Premium property {i+1} detected: {premium_info['premium_type']}")
        else:
            print(f"❌ Premium property {i+1} not detected")
    
    # Test standard properties
    for i, html in enumerate(standard_html_samples):
        soup = BeautifulSoup(html, 'html.parser')
        card = soup.find('div')
        
        premium_info = scraper.detect_premium_property_type(card)
        
        if not premium_info['is_premium']:
            standard_detected += 1
            print(f"✅ Standard property {i+1} correctly identified as non-premium")
        else:
            print(f"❌ Standard property {i+1} incorrectly detected as premium")
    
    scraper.close()
    
    print(f"\n📊 Detection Results:")
    print(f"   Premium properties detected: {premium_detected}/{len(premium_html_samples)}")
    print(f"   Standard properties detected: {standard_detected}/{len(standard_html_samples)}")
    
    return premium_detected == len(premium_html_samples) and standard_detected == len(standard_html_samples)

def test_enhanced_extraction_methods():
    """Test enhanced extraction methods"""
    print("\n🔧 Testing Enhanced Extraction Methods")
    print("-" * 50)
    
    # Initialize scraper
    scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=False)
    
    # Test HTML with various price formats
    test_html = '''
    <div class="mb-srp__card">
        <div class="mb-srp__card__price--amount">₹ 1.2 Cr</div>
        <div class="mb-srp__card__summary--value">1200 sqft</div>
        <h2 class="mb-srp__card--title">3 BHK Apartment</h2>
        <a href="/property-detail/apartment-123">View Details</a>
    </div>
    '''
    
    soup = BeautifulSoup(test_html, 'html.parser')
    card = soup.find('div', class_='mb-srp__card')
    
    # Test enhanced extraction
    title = scraper._extract_with_enhanced_fallback(
        card, scraper.premium_selectors['title'], 'title', 'N/A'
    )
    
    price = scraper._extract_with_enhanced_fallback(
        card, scraper.premium_selectors['price'], 'price', 'N/A'
    )
    
    area = scraper._extract_with_enhanced_fallback(
        card, scraper.premium_selectors['area'], 'area', 'N/A'
    )
    
    url = scraper._extract_premium_property_url(card)
    
    print(f"✅ Title extracted: {title}")
    print(f"✅ Price extracted: {price}")
    print(f"✅ Area extracted: {area}")
    print(f"✅ URL extracted: {url}")
    
    # Test validation logic (inline validation)
    is_valid = title != 'N/A' and (price != 'N/A' or area != 'N/A')
    print(f"✅ Data validation: {'Passed' if is_valid else 'Failed'}")
    
    scraper.close()
    
    return title != 'N/A' and price != 'N/A' and area != 'N/A' and url is not None

def test_extraction_statistics():
    """Test extraction statistics functionality"""
    print("\n📊 Testing Extraction Statistics")
    print("-" * 50)
    
    # Initialize scraper
    scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=False)
    
    # Get initial stats
    initial_stats = scraper.get_extraction_statistics()
    print(f"Initial stats: {initial_stats}")
    
    # Simulate some extractions
    scraper.extraction_stats['total_extracted'] = 100
    scraper.extraction_stats['successful_extractions'] = 85
    scraper.extraction_stats['failed_extractions'] = 15
    scraper.extraction_stats['premium_properties'] = 20
    scraper.extraction_stats['standard_properties'] = 80
    
    # Get updated stats
    updated_stats = scraper.get_extraction_statistics()
    print(f"\nUpdated stats:")
    print(f"   Total extracted: {updated_stats['total_extracted']}")
    print(f"   Success rate: {updated_stats['success_rate']:.1f}%")
    print(f"   Failure rate: {updated_stats['failure_rate']:.1f}%")
    print(f"   Premium percentage: {updated_stats['premium_percentage']:.1f}%")
    
    # Test reset
    scraper.reset_extraction_statistics()
    reset_stats = scraper.get_extraction_statistics()
    print(f"\nAfter reset: {reset_stats}")
    
    scraper.close()
    
    # Verify calculations
    expected_success_rate = 85.0
    expected_premium_percentage = 20.0
    
    success_rate_correct = abs(updated_stats['success_rate'] - expected_success_rate) < 0.1
    premium_percentage_correct = abs(updated_stats['premium_percentage'] - expected_premium_percentage) < 0.1
    reset_correct = reset_stats['total_extracted'] == 0
    
    return success_rate_correct and premium_percentage_correct and reset_correct

def test_premium_selectors_setup():
    """Test premium selectors setup"""
    print("\n⚙️ Testing Premium Selectors Setup")
    print("-" * 50)
    
    # Initialize scraper
    scraper = IntegratedMagicBricksScraper(headless=True, incremental_enabled=False)
    
    # Check if premium selectors are properly set up
    required_keys = ['title', 'price', 'area', 'url']
    
    all_keys_present = all(key in scraper.premium_selectors for key in required_keys)
    
    print(f"Premium selectors keys: {list(scraper.premium_selectors.keys())}")
    print(f"Required keys present: {all_keys_present}")
    
    # Check if selectors have content
    non_empty_selectors = all(
        len(scraper.premium_selectors[key]) > 0 for key in required_keys
    )
    
    print(f"All selectors have content: {non_empty_selectors}")
    
    # Print sample selectors
    for key in required_keys:
        selector_count = len(scraper.premium_selectors[key])
        print(f"   {key}: {selector_count} selectors")
    
    scraper.close()
    
    return all_keys_present and non_empty_selectors

def main():
    """Run all enhanced premium feature tests"""
    print("🧪 ENHANCED PREMIUM PROPERTY FEATURES TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Premium Property Detection", test_premium_property_detection),
        ("Enhanced Extraction Methods", test_enhanced_extraction_methods),
        ("Extraction Statistics", test_extraction_statistics),
        ("Premium Selectors Setup", test_premium_selectors_setup)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"\n{status}: {test_name}")
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"\n❌ ERROR in {test_name}: {str(e)}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for test_name, result, error in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if error:
            print(f"   Error: {error}")
    
    print(f"\n📊 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All enhanced premium features are working correctly!")
        return True
    else:
        print("⚠️ Some tests failed. Please review the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)