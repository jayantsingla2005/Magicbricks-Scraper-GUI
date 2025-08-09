#!/usr/bin/env python3
"""
Database Integration Testing Script
Tests database functionality and integration with the scraper.
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
    from src.database.database_manager import DatabaseManager
    from src.core.database_integrated_scraper import DatabaseIntegratedScraper
    from src.models.property_model import PropertyModel
except ImportError:
    print("❌ Import error - check module paths")
    sys.exit(1)

def test_database_functionality():
    """Test database manager functionality"""
    
    print("🗄️ Database Integration Testing")
    print("Testing database functionality and scraper integration")
    print("="*70)
    
    # Test configuration
    test_db_path = "test_magicbricks.db"
    test_url = "https://www.magicbricks.com/flats-in-gurgaon-for-sale-pppfs"
    
    results = {
        "test_config": {
            "db_path": test_db_path,
            "test_url": test_url,
            "timestamp": datetime.now().isoformat()
        },
        "database_manager": {},
        "scraper_integration": {},
        "performance": {}
    }
    
    # Clean up any existing test database
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    # Test 1: Database Manager Functionality
    print("\n🔧 Test 1: Database Manager Functionality")
    print("-" * 50)
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager(test_db_path)
        
        # Test session creation
        session_id = f"test_session_{int(time.time())}"
        session_created = db_manager.create_session(session_id, {"test": "config"})
        
        # Test property storage
        test_properties = create_test_properties(5)
        stored_count = db_manager.store_properties(test_properties, session_id, 1, test_url)
        
        # Test session update
        session_updated = db_manager.update_session(
            session_id,
            status='COMPLETED',
            total_properties=stored_count,
            end_time=datetime.now()
        )
        
        # Test data retrieval
        retrieved_properties = db_manager.get_properties(limit=10)
        
        # Test statistics
        stats = db_manager.get_statistics()
        
        # Test CSV export
        csv_export_path = "test_export.csv"
        csv_exported = db_manager.export_to_csv(csv_export_path)
        
        results["database_manager"] = {
            "initialization": True,
            "session_creation": session_created,
            "properties_stored": stored_count,
            "session_update": session_updated,
            "properties_retrieved": len(retrieved_properties),
            "statistics": stats,
            "csv_export": csv_exported,
            "success": True
        }
        
        print(f"✅ Database manager test completed successfully")
        print(f"   📊 Properties stored: {stored_count}")
        print(f"   📈 Properties retrieved: {len(retrieved_properties)}")
        print(f"   📋 Statistics: {stats.get('total_properties', 0)} total properties")
        
        # Cleanup
        db_manager.close()
        if os.path.exists(csv_export_path):
            os.remove(csv_export_path)
            
    except Exception as e:
        print(f"❌ Database manager test failed: {str(e)}")
        results["database_manager"]["error"] = str(e)
        results["database_manager"]["success"] = False
    
    # Test 2: Scraper Integration
    print("\n🔗 Test 2: Scraper Integration")
    print("-" * 50)
    
    try:
        # Create temporary config for database scraper
        db_config = create_test_config(test_url)
        
        # Initialize database-integrated scraper
        db_scraper = DatabaseIntegratedScraper(db_config, test_db_path, enable_db=True)
        
        # Test small scraping session with database storage
        start_time = time.time()
        scrape_result = db_scraper.scrape_all_pages_with_db(start_page=1, max_pages=2, store_batch_size=10)
        scrape_time = time.time() - start_time
        
        # Get database statistics
        db_stats = db_scraper.get_database_statistics()
        
        # Test database export
        db_export_path = "test_db_export.csv"
        export_success = db_scraper.export_from_database(db_export_path)
        
        results["scraper_integration"] = {
            "scraper_initialization": True,
            "scraping_success": scrape_result.get('success', False),
            "properties_scraped": scrape_result.get('total_properties', 0),
            "properties_stored": scrape_result.get('database_stats', {}).get('properties_stored', 0),
            "storage_errors": scrape_result.get('database_stats', {}).get('storage_errors', 0),
            "session_id": scrape_result.get('session_id'),
            "database_export": export_success,
            "scrape_time": scrape_time,
            "success": scrape_result.get('success', False)
        }
        
        print(f"✅ Scraper integration test completed")
        print(f"   📊 Properties scraped: {results['scraper_integration']['properties_scraped']}")
        print(f"   🗄️ Properties stored: {results['scraper_integration']['properties_stored']}")
        print(f"   ⏱️  Scrape time: {scrape_time:.1f}s")
        print(f"   🆔 Session ID: {results['scraper_integration']['session_id']}")
        
        # Cleanup
        if os.path.exists(db_config):
            os.remove(db_config)
        if os.path.exists(db_export_path):
            os.remove(db_export_path)
            
    except Exception as e:
        print(f"❌ Scraper integration test failed: {str(e)}")
        results["scraper_integration"]["error"] = str(e)
        results["scraper_integration"]["success"] = False
    
    # Test 3: Performance Analysis
    print("\n📊 Test 3: Performance Analysis")
    print("-" * 50)
    
    try:
        # Analyze database performance
        db_manager = DatabaseManager(test_db_path)
        
        # Test bulk insert performance
        bulk_properties = create_test_properties(50)
        
        start_time = time.time()
        bulk_stored = db_manager.store_properties(bulk_properties, "bulk_test", 1, test_url)
        bulk_time = time.time() - start_time
        
        # Test query performance
        start_time = time.time()
        query_results = db_manager.get_properties(limit=100)
        query_time = time.time() - start_time
        
        # Calculate performance metrics
        storage_rate = bulk_stored / bulk_time if bulk_time > 0 else 0
        query_rate = len(query_results) / query_time if query_time > 0 else 0
        
        results["performance"] = {
            "bulk_storage_time": bulk_time,
            "bulk_properties_stored": bulk_stored,
            "storage_rate_per_second": storage_rate,
            "query_time": query_time,
            "query_results": len(query_results),
            "query_rate_per_second": query_rate,
            "success": True
        }
        
        print(f"✅ Performance analysis completed")
        print(f"   🚀 Storage rate: {storage_rate:.1f} properties/second")
        print(f"   📈 Query rate: {query_rate:.1f} properties/second")
        print(f"   ⏱️  Bulk storage time: {bulk_time:.2f}s for {bulk_stored} properties")
        
        db_manager.close()
        
    except Exception as e:
        print(f"❌ Performance analysis failed: {str(e)}")
        results["performance"]["error"] = str(e)
        results["performance"]["success"] = False
    
    # Generate summary report
    print("\n" + "="*70)
    print("📊 DATABASE INTEGRATION SUMMARY")
    print("="*70)
    
    db_success = results["database_manager"].get("success", False)
    scraper_success = results["scraper_integration"].get("success", False)
    perf_success = results["performance"].get("success", False)
    
    print(f"🔧 Database Manager: {'✅ PASSED' if db_success else '❌ FAILED'}")
    print(f"🔗 Scraper Integration: {'✅ PASSED' if scraper_success else '❌ FAILED'}")
    print(f"📊 Performance Analysis: {'✅ PASSED' if perf_success else '❌ FAILED'}")
    
    overall_success = db_success and scraper_success and perf_success
    print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if overall_success else '⚠️ SOME TESTS FAILED'}")
    
    # Save detailed results
    output_file = f"database_integration_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {output_file}")
    print("🎯 Database Integration Testing Complete!")
    
    # Cleanup test database
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
        print(f"🧹 Cleaned up test database: {test_db_path}")
    
    return results

def create_test_properties(count: int) -> list:
    """Create test properties for database testing"""
    properties = []
    
    for i in range(count):
        prop = PropertyModel()
        prop.title = f"Test Property {i+1} - 3 BHK Apartment"
        prop.price = f"₹{1.5 + (i * 0.1):.1f} Cr"
        prop.super_area = f"{1200 + (i * 50)} sqft"
        prop.bedrooms = "3"
        prop.bathrooms = "2"
        prop.locality = f"Test Locality {(i % 5) + 1}"
        prop.city = "Gurgaon"
        prop.status = "Ready to Move"
        properties.append(prop)
    
    return properties

def create_test_config(test_url: str) -> str:
    """Create temporary configuration file for testing"""
    
    # Load base config
    with open("config/scraper_config.json", 'r') as f:
        base_config = json.load(f)
    
    # Update for test
    base_config['website']['base_url'] = test_url
    
    # Create temporary config file
    temp_config_path = f"temp_db_config_{int(time.time())}.json"
    with open(temp_config_path, 'w') as f:
        json.dump(base_config, f, indent=2)
    
    return temp_config_path

if __name__ == "__main__":
    print("🚀 Database Integration Testing Script")
    print("Testing database functionality and scraper integration...")
    print()
    
    try:
        results = test_database_functionality()
        
        # Determine overall success
        db_success = results.get("database_manager", {}).get("success", False)
        scraper_success = results.get("scraper_integration", {}).get("success", False)
        perf_success = results.get("performance", {}).get("success", False)
        
        if db_success and scraper_success and perf_success:
            print("\n✅ DATABASE INTEGRATION TESTING PASSED!")
            print("🎯 Database functionality and scraper integration working correctly")
        else:
            print("\n⚠️ DATABASE INTEGRATION TESTING INCOMPLETE")
            print("📊 Some tests failed - check results for details")
        
        print(f"📄 Check results file for detailed analysis")
        
    except Exception as e:
        print(f"❌ Database integration testing failed: {str(e)}")
        sys.exit(1)
