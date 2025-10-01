#!/usr/bin/env python3
"""
Test script to run MagicBricks scraper for exactly 3 pages
for real-time validation testing
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper, ScrapingMode

def main():
    """Run scraper for exactly 3 pages"""
    
    print("🎯 REAL-TIME VALIDATION TEST")
    print("=" * 50)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Target: Exactly 3 pages")
    print("🏙️ City: Gurgaon")
    print("=" * 50)
    
    try:
        # Initialize scraper
        scraper = IntegratedMagicBricksScraper(
            headless=True, 
            incremental_enabled=False
        )
        
        print("\n🚀 Starting 3-page scraping session...")
        
        # Run scraper for exactly 3 pages
        result = scraper.scrape_properties_with_incremental(
            city='gurgaon',
            mode=ScrapingMode.FULL,
            max_pages=3,  # Exactly 3 pages
            include_individual_pages=False,
            export_formats=['csv']
        )
        
        if result['success']:
            print(f"\n✅ SUCCESS! Scraping completed!")
            print(f"📊 Properties scraped: {result['properties_scraped']}")
            print(f"📄 Pages scraped: {result['pages_scraped']}")
            print(f"⏱️ Duration: {result.get('duration', 'N/A')}")
            
            if result.get('output_file'):
                print(f"💾 Data saved to: {result['output_file']}")
                
                # Show file info
                if os.path.exists(result['output_file']):
                    file_size = os.path.getsize(result['output_file'])
                    print(f"📁 File size: {file_size:,} bytes")
                    
                    # Count lines in CSV
                    with open(result['output_file'], 'r', encoding='utf-8') as f:
                        line_count = sum(1 for line in f)
                    print(f"📝 Total lines: {line_count:,} (including header)")
                    print(f"🏠 Properties in file: {line_count - 1:,}")
            
            print("\n🎯 Ready for manual validation!")
            print("📋 Next step: Manually check the same 3 pages on MagicBricks website")
            
        else:
            print(f"\n❌ FAILED! Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n💥 EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        if 'scraper' in locals():
            scraper.close()
            print("\n🔒 Scraper closed")

if __name__ == "__main__":
    main()
