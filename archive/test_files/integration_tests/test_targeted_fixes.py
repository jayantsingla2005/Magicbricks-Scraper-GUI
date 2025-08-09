#!/usr/bin/env python3
"""
Targeted Fixes Validation Testing Script
Tests specific fixes for area field mapping and society field extraction based on research findings.
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

try:
    from src.core.enhanced_field_extractor import EnhancedFieldExtractor
    from src.core.modern_scraper import ModernMagicBricksScraper
    from src.models.property_model import PropertyModel
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Import error - check module paths")
    sys.exit(1)

def test_area_field_mapping():
    """Test enhanced area field mapping with edge cases"""
    
    print("📐 Testing Enhanced Area Field Mapping")
    print("-" * 50)
    
    # Load configuration
    with open("config/scraper_config.json", 'r') as f:
        config = json.load(f)
    
    extractor = EnhancedFieldExtractor(config)
    
    # Test cases for area extraction
    test_cases = [
        {
            'name': 'Standard Apartment with Super Area',
            'html': '''
            <div>
                <h2>3 BHK Apartment for Sale</h2>
                <div>Super Area: 1,250 sqft</div>
                <div>Carpet Area: 1,000 sqft</div>
            </div>
            ''',
            'expected_super': '1,250 sqft',
            'expected_carpet': '1,000 sqft'
        },
        {
            'name': 'Plot with Square Yards',
            'html': '''
            <div>
                <h2>Residential Plot for Sale</h2>
                <div>Plot Area: 200 sqyrd</div>
            </div>
            ''',
            'expected_super': '1,800 sqft',  # 200 * 9
            'expected_carpet': None
        },
        {
            'name': 'House with Acres',
            'html': '''
            <div>
                <h2>Independent House for Sale</h2>
                <div>Land Area: 0.5 acres</div>
                <div>Carpet Area: 2,500 sqft</div>
            </div>
            ''',
            'expected_super': '21,780 sqft',  # 0.5 * 43,560
            'expected_carpet': '2,500 sqft'
        },
        {
            'name': 'Complex Area Format',
            'html': '''
            <div>
                <h2>2 BHK Flat for Sale</h2>
                <div>Super Area: 1,423.5 sq. ft</div>
            </div>
            ''',
            'expected_super': '1,424 sqft',  # Rounded
            'expected_carpet': None
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            soup = BeautifulSoup(test_case['html'], 'html.parser')
            property_data = extractor.extract_enhanced_property_data(soup, 1)
            
            # Check results
            super_match = property_data.super_area == test_case['expected_super']
            carpet_match = property_data.carpet_area == test_case['expected_carpet']
            
            result = {
                'name': test_case['name'],
                'super_area_extracted': property_data.super_area,
                'super_area_expected': test_case['expected_super'],
                'super_area_match': super_match,
                'carpet_area_extracted': property_data.carpet_area,
                'carpet_area_expected': test_case['expected_carpet'],
                'carpet_area_match': carpet_match,
                'overall_success': super_match and carpet_match
            }
            
            results.append(result)
            
            status = "✅" if result['overall_success'] else "❌"
            print(f"{status} {test_case['name']}")
            print(f"   Super Area: {property_data.super_area} (expected: {test_case['expected_super']})")
            print(f"   Carpet Area: {property_data.carpet_area} (expected: {test_case['expected_carpet']})")

            # Debug: Show extraction stats for failed tests
            if not result['overall_success']:
                stats = extractor.get_extraction_statistics()
                print(f"   Debug - Extraction stats: {stats['extraction_stats']['area_extractions']}")
            
        except Exception as e:
            print(f"❌ {test_case['name']}: Error - {str(e)}")
            results.append({'name': test_case['name'], 'overall_success': False, 'error': str(e)})
    
    # Summary
    successful_tests = sum(1 for r in results if r.get('overall_success', False))
    total_tests = len(test_cases)
    
    print(f"\n📊 Area Field Mapping Results: {successful_tests}/{total_tests} tests passed")
    
    return successful_tests == total_tests

def test_society_field_extraction():
    """Test enhanced society field extraction with edge cases"""
    
    print("\n🏢 Testing Enhanced Society Field Extraction")
    print("-" * 50)
    
    # Load configuration
    with open("config/scraper_config.json", 'r') as f:
        config = json.load(f)
    
    extractor = EnhancedFieldExtractor(config)
    
    # Test cases for society extraction
    test_cases = [
        {
            'name': 'Standard Apartment with Society Link',
            'html': '''
            <div>
                <h2>3 BHK Apartment for Sale</h2>
                <a href="/propertydetail/pdpid=123">DLF Cyber City</a>
                <div>Price: ₹1.5 Cr</div>
            </div>
            ''',
            'expected_society': 'DLF Cyber City'
        },
        {
            'name': 'Independent House without Society',
            'html': '''
            <div>
                <h2>Independent House for Sale in Sector 45</h2>
                <div>Located in Sector 45 Locality</div>
                <div>Price: ₹2.5 Cr</div>
            </div>
            ''',
            'expected_society_contains': 'Sector 45'
        },
        {
            'name': 'Plot with Area Name',
            'html': '''
            <div>
                <h2>Residential Plot for Sale</h2>
                <div>Plot in Green Valley Sector for sale</div>
                <div>Plot Area: 200 sqyrd</div>
            </div>
            ''',
            'expected_society_contains': 'Green Valley'
        },
        {
            'name': 'Apartment with Project Name in Title',
            'html': '''
            <div>
                <h2>2 BHK in Prestige Lakeside Habitat for Sale</h2>
                <div>Price: ₹85 Lac</div>
            </div>
            ''',
            'expected_society': 'Prestige Lakeside Habitat'
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            soup = BeautifulSoup(test_case['html'], 'html.parser')
            property_data = extractor.extract_enhanced_property_data(soup, 1)
            
            # Check results
            if 'expected_society' in test_case:
                society_match = property_data.society == test_case['expected_society']
            else:
                # Check if society contains expected text
                expected_text = test_case['expected_society_contains']
                society_match = (property_data.society and 
                               expected_text.lower() in property_data.society.lower())
            
            result = {
                'name': test_case['name'],
                'society_extracted': property_data.society,
                'society_expected': test_case.get('expected_society', f"Contains: {test_case.get('expected_society_contains')}"),
                'society_match': society_match,
                'overall_success': society_match
            }
            
            results.append(result)
            
            status = "✅" if result['overall_success'] else "❌"
            print(f"{status} {test_case['name']}")
            print(f"   Society: {property_data.society}")
            print(f"   Expected: {result['society_expected']}")
            
        except Exception as e:
            print(f"❌ {test_case['name']}: Error - {str(e)}")
            results.append({'name': test_case['name'], 'overall_success': False, 'error': str(e)})
    
    # Summary
    successful_tests = sum(1 for r in results if r.get('overall_success', False))
    total_tests = len(test_cases)
    
    print(f"\n📊 Society Field Extraction Results: {successful_tests}/{total_tests} tests passed")
    
    return successful_tests == total_tests

def test_property_type_detection():
    """Test enhanced property type detection"""
    
    print("\n🏠 Testing Enhanced Property Type Detection")
    print("-" * 50)
    
    # Load configuration
    with open("config/scraper_config.json", 'r') as f:
        config = json.load(f)
    
    extractor = EnhancedFieldExtractor(config)
    
    # Test cases for property type detection
    test_cases = [
        {
            'name': 'Residential Plot',
            'html': '<h2>Residential Plot for Sale in Sector 45</h2><div>Plot Area: 200 sqyrd</div>',
            'expected_type': 'plot'
        },
        {
            'name': 'Independent House',
            'html': '<h2>Independent House for Sale</h2><div>Carpet Area: 2000 sqft</div>',
            'expected_type': 'house'
        },
        {
            'name': 'Builder Floor',
            'html': '<h2>3 BHK Builder Floor for Sale</h2><div>Super Area: 1500 sqft</div>',
            'expected_type': 'floor'
        },
        {
            'name': 'Apartment',
            'html': '<h2>2 BHK Apartment for Sale</h2><div>Super Area: 1200 sqft</div>',
            'expected_type': 'apartment'
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            soup = BeautifulSoup(test_case['html'], 'html.parser')
            all_text = soup.get_text()
            
            # Test property type detection
            detected_type = extractor._detect_property_type_enhanced(soup, all_text)
            
            type_match = detected_type == test_case['expected_type']
            
            result = {
                'name': test_case['name'],
                'detected_type': detected_type,
                'expected_type': test_case['expected_type'],
                'type_match': type_match,
                'overall_success': type_match
            }
            
            results.append(result)
            
            status = "✅" if result['overall_success'] else "❌"
            print(f"{status} {test_case['name']}")
            print(f"   Detected: {detected_type}, Expected: {test_case['expected_type']}")
            
        except Exception as e:
            print(f"❌ {test_case['name']}: Error - {str(e)}")
            results.append({'name': test_case['name'], 'overall_success': False, 'error': str(e)})
    
    # Summary
    successful_tests = sum(1 for r in results if r.get('overall_success', False))
    total_tests = len(test_cases)
    
    print(f"\n📊 Property Type Detection Results: {successful_tests}/{total_tests} tests passed")
    
    return successful_tests == total_tests

def test_integration_with_scraper():
    """Test integration of enhanced extractor with main scraper"""
    
    print("\n🔗 Testing Integration with Main Scraper")
    print("-" * 50)
    
    try:
        # Create temporary config
        test_config = create_test_config()
        
        # Initialize scraper with enhanced extractor
        scraper = ModernMagicBricksScraper(test_config)
        
        # Verify enhanced extractor is initialized
        has_enhanced_extractor = hasattr(scraper, 'enhanced_extractor')
        extractor_type = type(scraper.enhanced_extractor).__name__ if has_enhanced_extractor else None
        
        # Get extraction statistics
        if has_enhanced_extractor:
            stats = scraper.enhanced_extractor.get_extraction_statistics()
        else:
            stats = {}
        
        print(f"✅ Enhanced extractor integration test completed")
        print(f"   Enhanced Extractor Present: {has_enhanced_extractor}")
        print(f"   Extractor Type: {extractor_type}")
        print(f"   Statistics Available: {bool(stats)}")
        
        # Cleanup
        if os.path.exists(test_config):
            os.remove(test_config)
        
        return has_enhanced_extractor and extractor_type == 'EnhancedFieldExtractor'
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return False

def create_test_config() -> str:
    """Create temporary configuration file for testing"""
    
    # Load base config
    with open("config/scraper_config.json", 'r') as f:
        base_config = json.load(f)
    
    # Create temporary config file
    temp_config_path = f"temp_targeted_fixes_config_{int(time.time())}.json"
    with open(temp_config_path, 'w') as f:
        json.dump(base_config, f, indent=2)
    
    return temp_config_path

def main():
    """Main testing function"""
    
    print("🎯 Targeted Fixes Validation Testing")
    print("Testing enhanced area mapping and society extraction...")
    print("="*70)
    
    results = {
        "area_field_mapping": False,
        "society_field_extraction": False,
        "property_type_detection": False,
        "scraper_integration": False
    }
    
    try:
        # Test 1: Area Field Mapping
        results["area_field_mapping"] = test_area_field_mapping()
        
        # Test 2: Society Field Extraction
        results["society_field_extraction"] = test_society_field_extraction()
        
        # Test 3: Property Type Detection
        results["property_type_detection"] = test_property_type_detection()
        
        # Test 4: Scraper Integration
        results["scraper_integration"] = test_integration_with_scraper()
        
        # Generate summary
        print("\n" + "="*70)
        print("📊 TARGETED FIXES VALIDATION SUMMARY")
        print("="*70)
        
        for test_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        overall_success = all(results.values())
        print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}")
        
        if overall_success:
            print("🎯 Targeted fixes successfully implemented and validated!")
            print("📈 Enhanced field extraction ready for production use")
        else:
            print("📊 Some fixes need attention - check test results above")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Targeted fixes testing failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Targeted Fixes Validation Testing")
    print("Testing specific fixes for area mapping and society extraction...")
    print()
    
    try:
        success = main()
        
        if success:
            print("\n✅ TARGETED FIXES VALIDATION PASSED!")
            print("🎯 Enhanced field extraction improvements validated")
        else:
            print("\n⚠️ TARGETED FIXES VALIDATION INCOMPLETE")
            print("📊 Some tests failed - check results for details")
        
    except Exception as e:
        print(f"❌ Targeted fixes validation failed: {str(e)}")
        sys.exit(1)
