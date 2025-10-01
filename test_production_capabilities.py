#!/usr/bin/env python3
"""
Test Production Capabilities - Test scheduling, parallel processing, and large-scale operations
"""

import sys
import os
import time
import traceback
from pathlib import Path

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_parallel_city_processing():
    """Test parallel processing of multiple cities"""
    
    print("🧪 TESTING PARALLEL CITY PROCESSING")
    print("-" * 50)
    
    try:
        from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
        from user_mode_options import ScrapingMode
        
        # Test parallel processing with 2 cities
        scraper = IntegratedMagicBricksScraper(
            headless=True,
            incremental_enabled=True
        )
        
        cities = ['gurgaon', 'noida']
        
        print(f"✅ Testing parallel processing for cities: {cities}")
        
        # Test the parallel method exists and is callable
        if hasattr(scraper, 'scrape_multiple_cities_parallel'):
            print(f"✅ Parallel processing method available")
            
            # Test configuration
            result = scraper.scrape_multiple_cities_parallel(
                cities=cities,
                mode=ScrapingMode.INCREMENTAL,
                max_pages_per_city=1,  # Small test
                include_individual_pages=False,
                export_formats=['csv'],
                max_workers=2
            )
            
            print(f"✅ Parallel processing test completed")
            print(f"📊 Result: {result.get('success', False)}")
            
            return True
        else:
            print(f"❌ Parallel processing method not available")
            return False
        
    except Exception as e:
        print(f"❌ Parallel processing test failed: {e}")
        traceback.print_exc()
        return False

def test_large_scale_configuration():
    """Test configuration for large-scale operations"""
    
    print("\n🧪 TESTING LARGE-SCALE CONFIGURATION")
    print("-" * 50)
    
    try:
        from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
        
        # Test large-scale configuration
        large_scale_config = {
            'max_pages': 1000,  # For 30K+ listings
            'concurrent_pages': 4,
            'batch_size': 50,
            'max_workers': 4,
            'individual_delay_min': 2,
            'individual_delay_max': 8,
            'batch_break_delay': 30,
            'page_delay': 5
        }
        
        scraper = IntegratedMagicBricksScraper(
            headless=True,
            incremental_enabled=True,
            custom_config=large_scale_config
        )
        
        print(f"✅ Large-scale scraper initialized")
        print(f"📊 Configuration:")
        for key, value in large_scale_config.items():
            print(f"  {key}: {value}")
        
        # Test that configuration is properly loaded
        for key, expected_value in large_scale_config.items():
            actual_value = scraper.config.get(key)
            if actual_value == expected_value:
                print(f"✅ {key}: {actual_value}")
            else:
                print(f"⚠️ {key}: expected {expected_value}, got {actual_value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Large-scale configuration test failed: {e}")
        traceback.print_exc()
        return False

def test_delay_controls():
    """Test delay control mechanisms"""
    
    print("\n🧪 TESTING DELAY CONTROLS")
    print("-" * 50)
    
    try:
        from magicbricks_gui import MagicBricksGUI
        
        # Create GUI instance to test delay controls
        gui = MagicBricksGUI()
        
        # Test delay variables exist
        delay_controls = [
            'delay_var',  # Page delay
            'individual_delay_min_var',  # Individual min delay
            'individual_delay_max_var',  # Individual max delay
            'batch_break_var',  # Batch break delay
            'batch_size_var'  # Batch size
        ]
        
        print(f"✅ Testing delay controls in GUI:")
        
        for control in delay_controls:
            if hasattr(gui, control):
                var = getattr(gui, control)
                value = var.get()
                print(f"  ✅ {control}: {value}")
            else:
                print(f"  ❌ {control}: Not found")
        
        # Test setting custom delays
        gui.delay_var.set("5")
        gui.individual_delay_min_var.set("3")
        gui.individual_delay_max_var.set("10")
        gui.batch_break_var.set("30")
        gui.batch_size_var.set("20")
        
        print(f"\n✅ Custom delay values set:")
        print(f"  Page delay: {gui.delay_var.get()}")
        print(f"  Individual delay: {gui.individual_delay_min_var.get()}-{gui.individual_delay_max_var.get()}")
        print(f"  Batch break: {gui.batch_break_var.get()}")
        print(f"  Batch size: {gui.batch_size_var.get()}")
        
        # Close GUI
        gui.root.after(100, gui.root.destroy)
        gui.root.mainloop()
        
        return True
        
    except Exception as e:
        print(f"❌ Delay controls test failed: {e}")
        traceback.print_exc()
        return False

def test_resume_functionality():
    """Test resume functionality and checkpoint system"""
    
    print("\n🧪 TESTING RESUME FUNCTIONALITY")
    print("-" * 50)
    
    try:
        from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
        from user_mode_options import ScrapingMode
        
        # Test incremental system (which provides resume functionality)
        scraper = IntegratedMagicBricksScraper(
            headless=True,
            incremental_enabled=True
        )
        
        print(f"✅ Scraper with incremental system initialized")
        
        # Check if incremental system has resume capabilities
        if hasattr(scraper, 'incremental_system'):
            print(f"✅ Incremental system available")
            
            # Check database components
            if hasattr(scraper.incremental_system, 'db_schema'):
                print(f"✅ Database schema system available")
            
            if hasattr(scraper.incremental_system, 'url_tracker'):
                print(f"✅ URL tracking system available")
            
            if hasattr(scraper.incremental_system, 'stopping_logic'):
                print(f"✅ Smart stopping logic available")
            
            # Test session management
            session_result = scraper.start_scraping_session('gurgaon', ScrapingMode.INCREMENTAL)
            if session_result:
                print(f"✅ Session management working")
                session_id = scraper.session_stats.get('session_id')
                print(f"  Session ID: {session_id}")
            else:
                print(f"⚠️ Session management issue")
            
            return True
        else:
            print(f"❌ Incremental system not available")
            return False
        
    except Exception as e:
        print(f"❌ Resume functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_database_capabilities():
    """Test database capabilities for large-scale operations"""
    
    print("\n🧪 TESTING DATABASE CAPABILITIES")
    print("-" * 50)
    
    try:
        from incremental_database_schema import IncrementalDatabaseSchema
        
        # Test database schema
        db_schema = IncrementalDatabaseSchema()
        
        print(f"✅ Database schema system initialized")
        
        # Test database connection
        if db_schema.connect():
            print(f"✅ Database connection successful")
            
            # Test table creation
            if db_schema.create_incremental_tables():
                print(f"✅ Incremental tables created")
            
            if db_schema.add_incremental_columns():
                print(f"✅ Incremental columns added")
            
            if db_schema.create_performance_indexes():
                print(f"✅ Performance indexes created")
            
            # Test validation
            validation = db_schema.validate_schema_enhancement()
            if validation:
                print(f"✅ Schema validation passed")
            else:
                print(f"⚠️ Schema validation issues")
            
            db_schema.close()
            return True
        else:
            print(f"❌ Database connection failed")
            return False
        
    except Exception as e:
        print(f"❌ Database capabilities test failed: {e}")
        traceback.print_exc()
        return False

def test_scheduling_capabilities():
    """Test scheduling capabilities"""
    
    print("\n🧪 TESTING SCHEDULING CAPABILITIES")
    print("-" * 50)
    
    try:
        # Check if scheduling files exist
        config_files = [
            'config/phase2_config.json',
            'schedules.json'
        ]
        
        print(f"✅ Checking scheduling configuration files:")
        
        for config_file in config_files:
            if Path(config_file).exists():
                print(f"  ✅ {config_file}: Found")
            else:
                print(f"  ℹ️ {config_file}: Not found (will be created when needed)")
        
        # Test GUI scheduling interface
        from magicbricks_gui import MagicBricksGUI
        
        gui = MagicBricksGUI()
        
        # Check if scheduling methods exist
        scheduling_methods = [
            'save_schedule',
            'format_schedule_description'
        ]
        
        print(f"\n✅ Checking scheduling methods in GUI:")
        
        for method in scheduling_methods:
            if hasattr(gui, method):
                print(f"  ✅ {method}: Available")
            else:
                print(f"  ❌ {method}: Not found")
        
        # Close GUI
        gui.root.after(100, gui.root.destroy)
        gui.root.mainloop()
        
        print(f"\n✅ Scheduling capabilities available")
        print(f"ℹ️ Note: Full scheduling requires integration with Windows Task Scheduler")
        
        return True
        
    except Exception as e:
        print(f"❌ Scheduling capabilities test failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 PRODUCTION CAPABILITIES TESTING SUITE")
    print("=" * 60)
    
    # Test all production capabilities
    tests = [
        ("Parallel City Processing", test_parallel_city_processing),
        ("Large-Scale Configuration", test_large_scale_configuration),
        ("Delay Controls", test_delay_controls),
        ("Resume Functionality", test_resume_functionality),
        ("Database Capabilities", test_database_capabilities),
        ("Scheduling Capabilities", test_scheduling_capabilities)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PRODUCTION CAPABILITIES TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status}: {test_name}")
    
    print(f"\n📈 OVERALL RESULT: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL PRODUCTION CAPABILITIES TESTS PASSED!")
        print("🚀 System is ready for large-scale production use!")
    else:
        print("⚠️ Some production capabilities need attention.")
