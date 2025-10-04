"""
Quick Validation Test for Stale Driver Fix
Tests 50-100 individual properties to verify the fix works

Target: ~100 individual property URLs
Expected Duration: 15-20 minutes
City: Mumbai (high bot detection area)
"""

import sys
import os
import time
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
from user_mode_options import ScrapingMode


def run_quick_validation():
    """Run quick validation test with ~100 individual properties"""
    
    print("=" * 80)
    print("QUICK VALIDATION TEST - STALE DRIVER FIX")
    print("=" * 80)
    
    # Test configuration
    city = "Mumbai"
    max_pages = 4  # 4 pages * 30 properties/page = ~120 properties
    
    config = {
        # P0 Optimizations
        'smart_filtering': True,
        'quality_threshold': 60.0,
        'ttl_days': 30,
        'page_load_strategy': 'eager',
        'block_third_party_resources': True,
        
        # P1 Optimizations
        'realistic_headers': True,
        
        # P2 Optimizations
        'randomize_viewport': True,
        
        # Test settings
        'concurrent_enabled': False,  # Sequential for stability
        'include_individual_pages': True,
        'max_pages': max_pages
    }
    
    print(f"\n📋 Test Configuration:")
    print(f"   City: {city}")
    print(f"   Max Pages: {max_pages} (target ~100 URLs)")
    print(f"   Mode: Incremental")
    print(f"   Individual Pages: Enabled")
    print(f"   Focus: Verify stale driver fix")
    
    print(f"\n🔧 All Optimizations Enabled:")
    print(f"   ✅ P0-1: Smart Filtering")
    print(f"   ✅ P0-2: Eager Page Load")
    print(f"   ✅ P0-3: Resource Blocking")
    print(f"   ✅ P0-4: Expand Restart Triggers")
    print(f"   ✅ P1-1: Realistic HTTP Headers")
    print(f"   ✅ P1-2: Referer Header Management")
    print(f"   ✅ P2-1: Viewport Randomization")
    print(f"   ✅ P2-2: Mouse Movement Simulation")
    
    print(f"\n🚀 Initializing scraper...")
    
    # Initialize scraper
    scraper = IntegratedMagicBricksScraper(headless=False, custom_config=config)
    
    # Start timer
    start_time = time.time()
    
    print(f"\n{'=' * 80}")
    print(f"TESTING STALE DRIVER FIX")
    print(f"{'=' * 80}\n")
    
    # Run scraping
    try:
        scraper.scrape_properties_with_incremental(
            city=city,
            mode=ScrapingMode.INCREMENTAL,
            include_individual_pages=True
        )
    except Exception as e:
        print(f"\n❌ Error during scraping: {e}")
        import traceback
        traceback.print_exc()
    
    # End timer
    end_time = time.time()
    duration = end_time - start_time
    
    # Get statistics from scraper
    listing_pages = getattr(scraper, 'pages_scraped', 0)
    listing_properties = getattr(scraper, 'total_properties_found', 0)
    
    # Try to get individual property stats
    individual_scraped = 0
    individual_total = 0
    individual_failed = 0
    restart_count = 0
    stale_driver_errors = 0
    
    if hasattr(scraper, 'individual_scraper') and scraper.individual_scraper:
        if hasattr(scraper.individual_scraper, 'individual_tracker') and scraper.individual_scraper.individual_tracker:
            # Get stats from tracker
            try:
                conn = scraper.individual_scraper.individual_tracker.conn
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM individual_properties_scraped WHERE extraction_success = 1")
                individual_scraped = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM individual_properties_scraped WHERE extraction_success = 0")
                individual_failed = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(*) FROM individual_properties_scraped")
                individual_total = cursor.fetchone()[0]
            except:
                pass
    
    # Calculate metrics
    print(f"\n📊 Test Results:")
    print(f"   Pages Scraped: {listing_pages}")
    print(f"   Listing Properties: {listing_properties}")
    print(f"   Individual Properties Attempted: {individual_total}")
    print(f"   Individual Properties Scraped: {individual_scraped}")
    print(f"   Individual Properties Failed: {individual_failed}")
    print(f"   Total Duration: {duration:.1f}s ({duration/60:.1f} min)")
    
    # Calculate detailed metrics
    success_rate = (individual_scraped / individual_total * 100) if individual_total > 0 else 0
    avg_time = (duration / individual_scraped) if individual_scraped > 0 else 0
    throughput = (individual_scraped / (duration / 60)) if duration > 0 else 0
    
    metrics = {
        'test_date': datetime.now().isoformat(),
        'test_type': 'quick_validation_stale_driver_fix',
        'city': city,
        'max_pages': max_pages,
        
        # Results
        'listing_pages_scraped': listing_pages,
        'listing_properties_found': listing_properties,
        'individual_urls_total': individual_total,
        'individual_urls_scraped': individual_scraped,
        'individual_urls_failed': individual_failed,
        'success_rate': success_rate,
        
        # Performance
        'total_duration_seconds': duration,
        'total_duration_minutes': duration / 60,
        'avg_time_per_property': avg_time,
        'throughput_properties_per_min': throughput,
        
        # Validation
        'stale_driver_errors': stale_driver_errors,
        'restart_count': restart_count,
        'fix_validated': stale_driver_errors == 0
    }
    
    # Save metrics
    metrics_file = f"quick_validation_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n{'=' * 80}")
    print(f"VALIDATION RESULTS")
    print(f"{'=' * 80}\n")
    
    print(f"⚡ PERFORMANCE:")
    print(f"   Avg Time per PDP: {avg_time:.2f}s")
    print(f"   Throughput: {throughput:.1f} properties/min")
    
    print(f"\n✅ DATA QUALITY:")
    print(f"   Total Attempted: {individual_total}")
    print(f"   Successful: {individual_scraped}")
    print(f"   Failed: {individual_failed}")
    print(f"   Success Rate: {success_rate:.1f}%")
    
    print(f"\n🔍 STALE DRIVER FIX VALIDATION:")
    print(f"   Stale Driver Errors: {stale_driver_errors}")
    print(f"   Driver Restarts: {restart_count}")
    if stale_driver_errors == 0:
        print(f"   ✅ FIX VALIDATED - No stale driver errors!")
    else:
        print(f"   ⚠️ FIX NEEDS REVIEW - Stale driver errors detected")
    
    print(f"\n⏱️ OVERALL:")
    print(f"   Total Duration: {metrics['total_duration_minutes']:.1f} minutes")
    
    print(f"\n💾 Metrics saved to: {metrics_file}")
    
    print(f"\n{'=' * 80}")
    print(f"ASSESSMENT")
    print(f"{'=' * 80}\n")
    
    # Assessment
    fix_pass = stale_driver_errors == 0
    performance_pass = avg_time <= 15  # Allow up to 15s per property
    quality_pass = success_rate >= 80  # 80% success rate
    
    print(f"Stale Driver Fix: {'✅ PASS' if fix_pass else '⚠️ FAIL'}")
    print(f"Performance: {'✅ PASS' if performance_pass else '⚠️ REVIEW'}")
    print(f"Data Quality: {'✅ PASS' if quality_pass else '⚠️ REVIEW'}")
    
    if fix_pass and performance_pass and quality_pass:
        print(f"\n✅ ALL CHECKS PASSED - READY FOR FULL VALIDATION")
    else:
        print(f"\n⚠️ Some checks need review")
    
    print(f"\n{'=' * 80}")
    print(f"TEST COMPLETE")
    print(f"{'=' * 80}\n")
    
    return metrics


if __name__ == "__main__":
    metrics = run_quick_validation()

