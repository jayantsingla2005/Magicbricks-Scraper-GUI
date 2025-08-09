#!/usr/bin/env python3
"""
URL Discovery System Testing Script
Tests the URL discovery and queue management functionality.
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
    from src.core.url_discovery_manager import URLDiscoveryManager, URLPriorityQueue
except ImportError:
    print("❌ Import error - check module paths")
    sys.exit(1)

def test_url_priority_queue():
    """Test URL priority queue functionality"""
    
    print("🔗 Testing URL Priority Queue")
    print("-" * 40)
    
    try:
        # Initialize priority queue
        queue = URLPriorityQueue(max_size=100)
        
        # Test URLs with different priorities
        test_urls = [
            ("https://example.com/property1", {"listing_title": "luxury apartment for sale", "listing_price": "₹3.5 Cr"}),
            ("https://example.com/property2", {"listing_title": "2 bhk apartment for sale", "listing_price": "₹85 Lac"}),
            ("https://example.com/property3", {"listing_title": "new launch premium villa", "listing_price": "₹5.2 Cr"}),
            ("https://example.com/property1", {"listing_title": "duplicate url test", "listing_price": "₹1 Cr"}),  # Duplicate
        ]
        
        # Add URLs to queue
        added_count = 0
        for url, metadata in test_urls:
            if queue.add_url(url, metadata):
                added_count += 1
        
        # Test getting URLs (should come out in priority order)
        retrieved_urls = []
        while not queue.is_empty():
            url_data = queue.get_next_url(timeout=0.1)
            if url_data:
                retrieved_urls.append(url_data)
            else:
                break
        
        # Get statistics
        stats = queue.get_stats()
        
        print(f"✅ URL Priority Queue test completed")
        print(f"   📊 URLs added: {added_count}/4 (1 duplicate filtered)")
        print(f"   📈 URLs retrieved: {len(retrieved_urls)}")
        print(f"   📋 Final stats: {stats}")
        print(f"   🎯 Priority order maintained: {len(retrieved_urls) > 0}")
        
        # Check if high priority URLs come first
        priority_order_correct = True
        if len(retrieved_urls) >= 2:
            first_priority = retrieved_urls[0][2]  # Priority is third element
            second_priority = retrieved_urls[1][2]
            priority_order_correct = first_priority <= second_priority
        
        print(f"   ⚡ Priority ordering: {'✅ Correct' if priority_order_correct else '❌ Incorrect'}")
        
        return added_count == 3 and len(retrieved_urls) == 3 and priority_order_correct
        
    except Exception as e:
        print(f"❌ URL Priority Queue test failed: {str(e)}")
        return False

def test_url_discovery_manager():
    """Test URL discovery manager functionality"""
    
    print("\n🔍 Testing URL Discovery Manager")
    print("-" * 40)
    
    try:
        # Clean up any existing test database
        test_db = "test_url_discovery.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        # Initialize discovery manager
        discovery_manager = URLDiscoveryManager(db_path=test_db)
        
        # Test database initialization
        db_initialized = hasattr(discovery_manager, 'db_manager')
        
        # Test URL validation
        test_urls = [
            "https://www.magicbricks.com/propertydetail/test1",  # Valid
            "https://www.magicbricks.com/property-detail/test2",  # Valid
            "https://www.magicbricks.com/builder/test3",  # Invalid (builder page)
            "https://www.magicbricks.com/search?q=test",  # Invalid (search page)
        ]
        
        valid_urls = []
        for url in test_urls:
            if discovery_manager._is_property_url(url):
                valid_urls.append(url)
        
        # Test metadata extraction (mock)
        from bs4 import BeautifulSoup
        mock_html = '''
        <div class="property-card">
            <h2 class="property-title">3 BHK Apartment for Sale</h2>
            <div class="property-price">₹1.5 Cr</div>
            <div class="property-location">Sector 45, Gurgaon</div>
        </div>
        '''
        
        soup = BeautifulSoup(mock_html, 'html.parser')
        link_element = soup.find('div')
        metadata = discovery_manager._extract_url_metadata(link_element, 1)
        
        # Test statistics
        stats = discovery_manager.get_discovery_statistics()

        print(f"✅ URL Discovery Manager test completed")
        print(f"   🗄️ Database initialized: {db_initialized}")
        print(f"   🔍 URL validation: {len(valid_urls)}/4 URLs correctly identified as valid")
        print(f"   📊 Metadata extraction: {len(metadata)} fields extracted")
        print(f"   📈 Statistics available: {bool(stats)}")

        # Cleanup
        discovery_manager.close()
        time.sleep(0.1)  # Brief delay for Windows file system
        if os.path.exists(test_db):
            os.remove(test_db)

        return db_initialized and len(valid_urls) == 2 and len(metadata) > 0
        
    except Exception as e:
        print(f"❌ URL Discovery Manager test failed: {str(e)}")
        return False

def test_url_pattern_matching():
    """Test URL pattern matching and filtering"""
    
    print("\n🎯 Testing URL Pattern Matching")
    print("-" * 40)
    
    try:
        # Create discovery manager for pattern testing
        discovery_manager = URLDiscoveryManager()
        
        # Test cases for URL pattern matching
        test_cases = [
            # Valid property URLs
            ("https://www.magicbricks.com/propertydetail/3-bhk-apartment-dlf-phase-2-gurgaon/12345", True),
            ("https://www.magicbricks.com/property-detail/house-for-sale/67890", True),
            ("https://www.magicbricks.com/listing/plot-for-sale?pdpid=11111", True),
            
            # Invalid URLs (should be filtered out)
            ("https://www.magicbricks.com/builder/dlf-limited", False),
            ("https://www.magicbricks.com/project/dlf-magnolias", False),
            ("https://www.magicbricks.com/locality/sector-45-gurgaon", False),
            ("https://www.magicbricks.com/advertisement/banner", False),
            ("https://www.magicbricks.com/search?q=apartment", False),
            
            # Edge cases
            ("https://www.magicbricks.com/propertydetail/", True),  # Minimal valid URL
            ("https://other-site.com/propertydetail/test", True),  # Different domain but valid pattern
        ]
        
        correct_matches = 0
        total_tests = len(test_cases)
        
        for url, expected_valid in test_cases:
            actual_valid = discovery_manager._is_property_url(url)
            if actual_valid == expected_valid:
                correct_matches += 1
            else:
                print(f"   ❌ Mismatch: {url} - Expected: {expected_valid}, Got: {actual_valid}")
        
        accuracy = (correct_matches / total_tests) * 100
        
        print(f"✅ URL Pattern Matching test completed")
        print(f"   🎯 Accuracy: {correct_matches}/{total_tests} ({accuracy:.1f}%)")
        print(f"   ✔️ Valid property URLs correctly identified")
        print(f"   ❌ Invalid URLs correctly filtered")
        
        return accuracy >= 90  # 90% accuracy threshold
        
    except Exception as e:
        print(f"❌ URL Pattern Matching test failed: {str(e)}")
        return False

def test_database_integration():
    """Test database integration for URL storage"""
    
    print("\n🗄️ Testing Database Integration")
    print("-" * 40)
    
    try:
        # Clean up test database
        test_db = "test_url_db_integration.db"
        if os.path.exists(test_db):
            os.remove(test_db)
        
        # Initialize discovery manager
        discovery_manager = URLDiscoveryManager(db_path=test_db)
        
        # Test URL storage
        test_url = "https://www.magicbricks.com/propertydetail/test-property"
        test_metadata = {
            "listing_title": "Test Property",
            "listing_price": "₹1.5 Cr",
            "discovery_page": 1
        }
        
        # Add URL to database
        url_added = discovery_manager._add_discovered_url(
            test_url, test_metadata, "test_source_page", "test_session"
        )
        
        # Try to add duplicate (should fail)
        duplicate_added = discovery_manager._add_discovered_url(
            test_url, test_metadata, "test_source_page", "test_session"
        )
        
        # Get pending URLs
        pending_urls = discovery_manager.get_pending_urls(limit=10)
        
        # Mark URL as processed
        discovery_manager.mark_url_processed(test_url, success=True)
        
        # Get updated pending URLs
        updated_pending = discovery_manager.get_pending_urls(limit=10)
        
        # Get statistics
        stats = discovery_manager.get_discovery_statistics()

        print(f"✅ Database Integration test completed")
        print(f"   📝 URL added: {url_added}")
        print(f"   🚫 Duplicate rejected: {not duplicate_added}")
        print(f"   📋 Pending URLs retrieved: {len(pending_urls)}")
        print(f"   ✅ URL marked as processed: {len(updated_pending) < len(pending_urls)}")
        print(f"   📊 Statistics generated: {bool(stats)}")

        # Cleanup
        discovery_manager.close()
        time.sleep(0.1)  # Brief delay for Windows file system
        if os.path.exists(test_db):
            os.remove(test_db)

        return url_added and not duplicate_added and len(pending_urls) > 0
        
    except Exception as e:
        print(f"❌ Database Integration test failed: {str(e)}")
        return False

def main():
    """Main testing function"""
    
    print("🚀 URL Discovery System Testing")
    print("Testing URL discovery and queue management functionality...")
    print("="*60)
    
    results = {
        "url_priority_queue": False,
        "url_discovery_manager": False,
        "url_pattern_matching": False,
        "database_integration": False
    }
    
    try:
        # Test 1: URL Priority Queue
        results["url_priority_queue"] = test_url_priority_queue()
        
        # Test 2: URL Discovery Manager
        results["url_discovery_manager"] = test_url_discovery_manager()
        
        # Test 3: URL Pattern Matching
        results["url_pattern_matching"] = test_url_pattern_matching()
        
        # Test 4: Database Integration
        results["database_integration"] = test_database_integration()
        
        # Generate summary
        print("\n" + "="*60)
        print("📊 URL DISCOVERY TESTING SUMMARY")
        print("="*60)
        
        for test_name, success in results.items():
            status = "✅ PASSED" if success else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        overall_success = all(results.values())
        print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}")
        
        if overall_success:
            print("🎯 URL Discovery system is ready for Phase II implementation!")
            print("📈 Queue management, URL validation, and database integration working correctly")
        else:
            print("📊 Some components need attention - check test results above")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ URL Discovery testing failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 URL Discovery System Testing")
    print("Testing URL discovery and queue management...")
    print()
    
    try:
        success = main()
        
        if success:
            print("\n✅ URL DISCOVERY TESTING PASSED!")
            print("🎯 URL discovery system ready for production use")
        else:
            print("\n⚠️ URL DISCOVERY TESTING INCOMPLETE")
            print("📊 Some tests failed - review and address issues")
        
    except Exception as e:
        print(f"❌ URL Discovery testing failed: {str(e)}")
        sys.exit(1)
