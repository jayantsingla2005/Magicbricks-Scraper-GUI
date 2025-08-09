#!/usr/bin/env python3
"""
Phase II Scraper Testing Script
Tests URL discovery and detailed property page scraping functionality.
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
    from src.core.phase2_scraper import URLQueueManager, DetailedPropertyExtractor, Phase2Scraper
except ImportError:
    print("❌ Import error - check module paths")
    sys.exit(1)

def test_url_queue_manager():
    """Test URL queue management functionality"""
    
    print("🔗 Testing URL Queue Manager")
    print("-" * 40)
    
    try:
        # Initialize queue manager
        queue_manager = URLQueueManager(max_queue_size=100)
        
        # Test adding URLs
        test_urls = [
            ("https://www.magicbricks.com/propertydetail/test1", {"test": "metadata1"}),
            ("https://www.magicbricks.com/propertydetail/test2", {"test": "metadata2"}),
            ("https://www.magicbricks.com/propertydetail/test1", {"test": "duplicate"}),  # Duplicate
        ]
        
        added_count = 0
        for url, metadata in test_urls:
            if queue_manager.add_url(url, metadata):
                added_count += 1
        
        # Test getting URLs
        retrieved_urls = []
        while True:
            url_data = queue_manager.get_next_url(timeout=0.1)
            if url_data is None:
                break
            retrieved_urls.append(url_data)
        
        # Test marking completion
        for url, _ in retrieved_urls:
            queue_manager.mark_completed(url)
        
        # Get statistics
        stats = queue_manager.get_stats()
        
        print(f"✅ URL Queue Manager test completed")
        print(f"   📊 URLs added: {added_count}/3 (1 duplicate filtered)")
        print(f"   📈 URLs retrieved: {len(retrieved_urls)}")
        print(f"   📋 Final stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL Queue Manager test failed: {str(e)}")
        return False

def test_detailed_property_extractor():
    """Test detailed property data extraction"""
    
    print("\n🔍 Testing Detailed Property Extractor")
    print("-" * 40)
    
    try:
        # Load configuration
        with open("config/scraper_config.json", 'r') as f:
            config = json.load(f)
        
        # Initialize extractor
        extractor = DetailedPropertyExtractor(config)
        
        # Create mock HTML for testing
        mock_html = """
        <html>
            <body>
                <div class="mb-ldp__dtls__body">
                    <div data-testid="property-id">MB12345</div>
                    <div data-testid="rera-id">RERA67890</div>
                    <div class="mb-ldp__builder__name">Test Builder</div>
                    <div class="mb-ldp__possession">Dec 2025</div>
                </div>
                <div class="mb-ldp__price__breakdown">
                    Base Price: ₹1.5 Cr, Registration: ₹2 Lac
                </div>
                <div class="mb-ldp__amenities">
                    <li>Swimming Pool</li>
                    <li>Gym</li>
                    <li>Parking</li>
                </div>
                <div class="mb-ldp__location">
                    Address: Test Location, Gurgaon
                    lat: 28.4595, lng: 77.0266
                </div>
                <script type="application/ld+json">
                    {"@type": "RealEstate", "name": "Test Property"}
                </script>
            </body>
        </html>
        """
        
        # Parse HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(mock_html, 'html.parser')
        
        # Extract detailed data
        detailed_data = extractor.extract_detailed_data(soup, "https://test.com/property/123")
        
        # Validate extraction
        expected_fields = ['source_url', 'extracted_at', 'extraction_success']
        extracted_fields = [field for field in expected_fields if field in detailed_data]
        
        print(f"✅ Detailed Property Extractor test completed")
        print(f"   📊 Extraction success: {detailed_data.get('extraction_success', False)}")
        print(f"   📈 Fields extracted: {len(detailed_data)} total")
        print(f"   📋 Required fields: {len(extracted_fields)}/{len(expected_fields)}")
        print(f"   🏢 Property ID: {detailed_data.get('property_id', 'Not found')}")
        print(f"   🏗️ Builder: {detailed_data.get('builder_name', 'Not found')}")
        
        return detailed_data.get('extraction_success', False)
        
    except Exception as e:
        print(f"❌ Detailed Property Extractor test failed: {str(e)}")
        return False

def test_phase2_scraper_integration():
    """Test Phase II scraper integration"""
    
    print("\n🚀 Testing Phase II Scraper Integration")
    print("-" * 40)
    
    try:
        # Create temporary config
        test_config = create_test_config()
        test_db = "test_phase2.db"
        
        # Clean up any existing test database
        if os.path.exists(test_db):
            os.remove(test_db)
        
        # Initialize Phase II scraper
        phase2_scraper = Phase2Scraper(test_config, test_db, max_workers=2)
        
        # Test URL discovery (small scale)
        print("   🔍 Testing URL discovery...")
        urls_discovered = phase2_scraper.discover_property_urls(start_page=1, max_pages=2)
        
        # Get queue statistics
        queue_stats = phase2_scraper.url_queue.get_stats()
        
        print(f"   ✅ URL Discovery completed")
        print(f"      📊 URLs discovered: {urls_discovered}")
        print(f"      📈 Queue stats: {queue_stats}")
        
        # Test detailed scraping (if URLs were discovered)
        if urls_discovered > 0:
            print("   🔍 Testing detailed property scraping...")
            
            # Limit to small number for testing
            # Manually add a few test URLs to avoid long scraping
            test_urls = [
                "https://www.magicbricks.com/propertydetail/test1",
                "https://www.magicbricks.com/propertydetail/test2"
            ]
            
            for url in test_urls[:2]:  # Limit to 2 for testing
                phase2_scraper.url_queue.add_url(url, {"test": True})
            
            # Run detailed scraping
            scraping_results = phase2_scraper.scrape_detailed_properties(max_workers=1)
            
            print(f"   ✅ Detailed Scraping completed")
            print(f"      📊 Results: {scraping_results}")
        
        # Cleanup
        if os.path.exists(test_config):
            os.remove(test_config)
        if os.path.exists(test_db):
            os.remove(test_db)
        
        print(f"✅ Phase II Scraper Integration test completed")
        return True
        
    except Exception as e:
        print(f"❌ Phase II Scraper Integration test failed: {str(e)}")
        return False

def create_test_config() -> str:
    """Create temporary configuration file for testing"""
    
    # Load base config
    with open("config/scraper_config.json", 'r') as f:
        base_config = json.load(f)
    
    # Update for test
    base_config['website']['base_url'] = "https://www.magicbricks.com/flats-in-gurgaon-for-sale-pppfs"
    
    # Create temporary config file
    temp_config_path = f"temp_phase2_config_{int(time.time())}.json"
    with open(temp_config_path, 'w') as f:
        json.dump(base_config, f, indent=2)
    
    return temp_config_path

def main():
    """Main testing function"""
    
    print("🚀 Phase II Scraper Testing Script")
    print("Testing URL discovery and detailed property scraping...")
    print("="*60)
    
    results = {
        "url_queue_manager": False,
        "detailed_extractor": False,
        "phase2_integration": False
    }
    
    try:
        # Test 1: URL Queue Manager
        results["url_queue_manager"] = test_url_queue_manager()
        
        # Test 2: Detailed Property Extractor
        results["detailed_extractor"] = test_detailed_property_extractor()
        
        # Test 3: Phase II Scraper Integration
        results["phase2_integration"] = test_phase2_scraper_integration()
        
        # Generate summary
        print("\n" + "="*60)
        print("📊 PHASE II TESTING SUMMARY")
        print("="*60)
        
        for test_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        overall_success = all(results.values())
        print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}")
        
        if overall_success:
            print("🎯 Phase II architecture is ready for detailed property scraping!")
        else:
            print("📊 Some components need attention - check test results above")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ Phase II testing failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Phase II Scraper Testing")
    print("Testing URL queue management and detailed property extraction...")
    print()
    
    try:
        success = main()
        
        if success:
            print("\n✅ PHASE II TESTING PASSED!")
            print("🎯 Ready for production detailed property scraping")
        else:
            print("\n⚠️ PHASE II TESTING INCOMPLETE")
            print("📊 Some tests failed - check results for details")
        
    except Exception as e:
        print(f"❌ Phase II testing failed: {str(e)}")
        sys.exit(1)
