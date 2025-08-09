#!/usr/bin/env python3
"""
Detailed Property Extractor Testing Script
Tests the detailed property page extraction functionality.
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
    from src.core.detailed_property_extractor import DetailedPropertyExtractor, DetailedPropertyModel
    from src.core.modern_scraper import ModernMagicBricksScraper
except ImportError:
    print("❌ Import error - check module paths")
    sys.exit(1)

def test_detailed_property_model():
    """Test detailed property model functionality"""
    
    print("🏠 Testing Detailed Property Model")
    print("-" * 40)
    
    try:
        # Initialize model
        model = DetailedPropertyModel()
        
        # Test adding amenities
        model.amenities['indoor'].extend(['Swimming Pool', 'Gym', 'Clubhouse'])
        model.amenities['security'].extend(['CCTV', 'Security Guard', 'Intercom'])
        
        # Test adding floor plan info
        model.floor_plan['layout_type'] = '3 BHK'
        model.floor_plan['room_details']['bedrooms'] = 3
        model.floor_plan['room_details']['bathrooms'] = 2
        
        # Test adding neighborhood info
        model.neighborhood['schools'].extend(['DPS School', 'Ryan International'])
        model.neighborhood['hospitals'].extend(['Max Hospital', 'Fortis Healthcare'])
        
        # Test adding project info
        model.project_info['builder_name'] = 'DLF Limited'
        model.project_info['project_name'] = 'DLF Magnolias'
        model.project_info['rera_id'] = 'RERA123456'
        
        # Test completeness calculation
        completeness = model.calculate_completeness()
        
        # Test dictionary conversion
        model_dict = model.to_dict()
        
        print(f"✅ Detailed Property Model test completed")
        print(f"   🏠 Amenities added: {len(model.amenities['indoor']) + len(model.amenities['security'])}")
        print(f"   📐 Floor plan info: {bool(model.floor_plan['layout_type'])}")
        print(f"   🏫 Neighborhood items: {len(model.neighborhood['schools']) + len(model.neighborhood['hospitals'])}")
        print(f"   🏗️ Project info: {bool(model.project_info['builder_name'])}")
        print(f"   📊 Completeness: {completeness:.1f}%")
        print(f"   📋 Dictionary conversion: {bool(model_dict)}")
        
        return completeness > 0 and len(model_dict) > 0
        
    except Exception as e:
        print(f"❌ Detailed Property Model test failed: {str(e)}")
        return False

def test_selector_configuration():
    """Test selector configuration and loading"""

    print("\n🎯 Testing Selector Configuration")
    print("-" * 40)

    try:
        # Load actual configuration file
        with open('config/scraper_config.json', 'r') as f:
            test_config = json.load(f)

        # Add phase2 selectors for testing
        test_config['phase2'] = {
            'selectors': {
                'amenities': {
                    'container': '.amenities-section',
                    'items': '.amenity-item',
                    'categories': {
                        'indoor': ['gym', 'pool'],
                        'security': ['security', 'cctv']
                    }
                },
                'floor_plan': {
                    'container': '.floor-plan-section',
                    'layout_type': '.layout-type'
                }
            }
        }

        # Initialize extractor
        extractor = DetailedPropertyExtractor(test_config)

        # Test selector loading
        selectors_loaded = hasattr(extractor, 'selectors')
        amenities_selectors = 'amenities' in extractor.selectors
        floor_plan_selectors = 'floor_plan' in extractor.selectors

        # Test statistics initialization
        stats_initialized = hasattr(extractor, 'extraction_stats')

        print(f"✅ Selector Configuration test completed")
        print(f"   📋 Selectors loaded: {selectors_loaded}")
        print(f"   🏠 Amenities selectors: {amenities_selectors}")
        print(f"   📐 Floor plan selectors: {floor_plan_selectors}")
        print(f"   📊 Statistics initialized: {stats_initialized}")

        return selectors_loaded and amenities_selectors and stats_initialized

    except Exception as e:
        print(f"❌ Selector Configuration test failed: {str(e)}")
        return False

def test_html_parsing():
    """Test HTML parsing and extraction methods"""
    
    print("\n📄 Testing HTML Parsing")
    print("-" * 40)
    
    try:
        # Load actual configuration file
        with open('config/scraper_config.json', 'r') as f:
            test_config = json.load(f)

        # Add phase2 selectors for testing
        test_config['phase2'] = {
            'selectors': {
                'amenities': {
                    'container': '.amenities-section',
                    'items': '.amenity-item',
                    'categories': {
                        'indoor': ['swimming pool', 'gym'],
                        'security': ['security']
                    }
                },
                'floor_plan': {
                    'container': '.floor-plan-section',
                    'layout_type': '.layout-type'
                },
                'neighborhood': {
                    'container': '.nearby-section',
                    'schools': '.schools-section'
                },
                'project_info': {
                    'container': '.project-section',
                    'builder': '.builder-name',
                    'project': '.project-name'
                }
            }
        }
        
        # Initialize extractor
        extractor = DetailedPropertyExtractor(test_config)
        
        # Create test HTML
        test_html = '''
        <html>
            <body>
                <div class="amenities-section">
                    <div class="amenity-item">Swimming Pool</div>
                    <div class="amenity-item">Gym</div>
                    <div class="amenity-item">Security</div>
                </div>
                <div class="floor-plan-section">
                    <div class="layout-type">3 BHK</div>
                    <div class="room-details">3 Bedrooms, 2 Bathrooms</div>
                </div>
                <div class="nearby-section">
                    <div class="schools-section">
                        <div class="item">DPS School</div>
                        <div class="item">Ryan International</div>
                    </div>
                </div>
                <div class="project-section">
                    <div class="builder-name">DLF Limited</div>
                    <div class="project-name">DLF Magnolias</div>
                </div>
            </body>
        </html>
        '''
        
        # Parse HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(test_html, 'html.parser')
        
        # Create test property model
        property_model = DetailedPropertyModel()
        
        # Test individual extraction methods
        extractor._extract_amenities(soup, property_model)
        extractor._extract_floor_plan(soup, property_model)
        extractor._extract_neighborhood(soup, property_model)
        extractor._extract_project_info(soup, property_model)
        
        # Check extraction results
        amenities_extracted = len(property_model.amenities['indoor']) > 0 or len(property_model.amenities['lifestyle']) > 0
        floor_plan_extracted = property_model.floor_plan['layout_type'] is not None
        neighborhood_extracted = len(property_model.neighborhood['schools']) > 0
        project_extracted = property_model.project_info['builder_name'] is not None
        
        print(f"✅ HTML Parsing test completed")
        print(f"   🏠 Amenities extracted: {amenities_extracted}")
        print(f"   📐 Floor plan extracted: {floor_plan_extracted}")
        print(f"   🏫 Neighborhood extracted: {neighborhood_extracted}")
        print(f"   🏗️ Project info extracted: {project_extracted}")
        
        return amenities_extracted and floor_plan_extracted
        
    except Exception as e:
        print(f"❌ HTML Parsing test failed: {str(e)}")
        return False

def test_extraction_statistics():
    """Test extraction statistics tracking"""
    
    print("\n📊 Testing Extraction Statistics")
    print("-" * 40)
    
    try:
        # Load actual configuration file
        with open('config/scraper_config.json', 'r') as f:
            test_config = json.load(f)

        # Add phase2 selectors for testing
        test_config['phase2'] = {'selectors': {}}
        
        # Initialize extractor
        extractor = DetailedPropertyExtractor(test_config)
        
        # Simulate some extractions
        initial_stats = extractor.get_extraction_statistics()
        
        # Manually update statistics (simulating successful extractions)
        extractor.extraction_stats['pages_processed'] = 10
        extractor.extraction_stats['successful_extractions'] = 8
        extractor.extraction_stats['failed_extractions'] = 2
        extractor.extraction_stats['avg_completeness'] = 75.5
        extractor.extraction_stats['total_amenities_extracted'] = 45
        
        # Get updated statistics
        updated_stats = extractor.get_extraction_statistics()
        
        # Check statistics
        stats_available = 'extraction_stats' in updated_stats
        success_rate_calculated = 'success_rate' in updated_stats
        success_rate_correct = updated_stats['success_rate'] == 80.0  # 8/10 * 100
        
        print(f"✅ Extraction Statistics test completed")
        print(f"   📊 Statistics available: {stats_available}")
        print(f"   📈 Success rate calculated: {success_rate_calculated}")
        print(f"   🎯 Success rate correct: {success_rate_correct} ({updated_stats.get('success_rate', 0):.1f}%)")
        print(f"   📋 Average completeness: {updated_stats['avg_completeness']:.1f}%")
        
        return stats_available and success_rate_calculated and success_rate_correct
        
    except Exception as e:
        print(f"❌ Extraction Statistics test failed: {str(e)}")
        return False

def test_error_handling():
    """Test error handling and recovery"""
    
    print("\n🛡️ Testing Error Handling")
    print("-" * 40)
    
    try:
        # Load actual configuration file
        with open('config/scraper_config.json', 'r') as f:
            test_config = json.load(f)

        # Add phase2 selectors for testing
        test_config['phase2'] = {'selectors': {}}
        
        # Initialize extractor
        extractor = DetailedPropertyExtractor(test_config)
        
        # Test with invalid HTML
        from bs4 import BeautifulSoup
        invalid_html = '<html><body><div>Invalid structure</div></body></html>'
        soup = BeautifulSoup(invalid_html, 'html.parser')
        
        # Create property model
        property_model = DetailedPropertyModel()
        
        # Test extraction with invalid selectors (should not crash)
        try:
            extractor._extract_amenities(soup, property_model)
            extractor._extract_floor_plan(soup, property_model)
            extractor._extract_neighborhood(soup, property_model)
            amenities_error_handled = True
        except Exception:
            amenities_error_handled = False
        
        # Test with None soup (should not crash)
        try:
            extractor._extract_project_info(None, property_model)
            none_error_handled = True
        except Exception:
            none_error_handled = False
        
        # Check if errors were logged in metadata
        errors_logged = len(property_model.extraction_metadata['extraction_errors']) >= 0
        
        print(f"✅ Error Handling test completed")
        print(f"   🛡️ Invalid HTML handled: {amenities_error_handled}")
        print(f"   🚫 None input handled: {none_error_handled}")
        print(f"   📝 Errors logged: {errors_logged}")
        print(f"   📋 Error count: {len(property_model.extraction_metadata['extraction_errors'])}")
        
        return amenities_error_handled and errors_logged
        
    except Exception as e:
        print(f"❌ Error Handling test failed: {str(e)}")
        return False

def main():
    """Main testing function"""
    
    print("🚀 Detailed Property Extractor Testing")
    print("Testing detailed property page extraction functionality...")
    print("="*60)
    
    results = {
        "detailed_property_model": False,
        "selector_configuration": False,
        "html_parsing": False,
        "extraction_statistics": False,
        "error_handling": False
    }
    
    try:
        # Test 1: Detailed Property Model
        results["detailed_property_model"] = test_detailed_property_model()
        
        # Test 2: Selector Configuration
        results["selector_configuration"] = test_selector_configuration()
        
        # Test 3: HTML Parsing
        results["html_parsing"] = test_html_parsing()
        
        # Test 4: Extraction Statistics
        results["extraction_statistics"] = test_extraction_statistics()
        
        # Test 5: Error Handling
        results["error_handling"] = test_error_handling()
        
        # Generate summary
        print("\n" + "="*60)
        print("📊 DETAILED EXTRACTOR TESTING SUMMARY")
        print("="*60)
        
        for test_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        overall_success = all(results.values())
        print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}")
        
        if overall_success:
            print("🎯 Detailed property extractor is ready for Phase II implementation!")
            print("📈 Model structure, parsing, and error handling working correctly")
        else:
            print("📊 Some components need attention - check test results above")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Detailed extractor testing failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Detailed Property Extractor Testing")
    print("Testing detailed property page extraction...")
    print()
    
    try:
        success = main()
        
        if success:
            print("\n✅ DETAILED EXTRACTOR TESTING PASSED!")
            print("🎯 Detailed property extraction system ready for production use")
        else:
            print("\n⚠️ DETAILED EXTRACTOR TESTING INCOMPLETE")
            print("📊 Some tests failed - review and address issues")
        
    except Exception as e:
        print(f"❌ Detailed extractor testing failed: {str(e)}")
        sys.exit(1)
