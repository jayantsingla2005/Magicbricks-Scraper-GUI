#!/usr/bin/env python3
"""
Test Enhanced Fields in MagicBricks Scraper
Tests the 4 new high-priority fields added in Phase 3
"""

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
import pandas as pd

def test_enhanced_fields():
    """Test the enhanced scraper with new fields"""
    
    # Create scraper instance
    scraper = IntegratedMagicBricksScraper()
    
    # Test with just 1 page
    print('🧪 Testing enhanced scraper with 1 page...')
    result = scraper.scrape_properties_with_incremental(
        city='gurgaon',
        max_pages=1,
        export_formats=['csv']
    )
    
    print(f'✅ Scraped {len(scraper.properties)} properties')
    
    # Check if new fields are present
    if scraper.properties:
        sample_property = scraper.properties[0]
        print('\n🎯 New fields in scraped data:')
        new_fields = ['photo_count', 'owner_name', 'contact_options', 'description']
        
        for field in new_fields:
            value = sample_property.get(field, 'NOT FOUND')
            status = '✅' if value and value != 'NOT FOUND' and value.strip() else '❌'
            print(f'  {status} {field}: {value}')
        
        # Save to test file
        df = pd.DataFrame(scraper.properties)
        df.to_csv('enhanced_test_sample.csv', index=False)
        print(f'\n💾 Saved sample to enhanced_test_sample.csv')
        print(f'📊 Total columns: {len(df.columns)}')
        
        # Check which new fields are present in columns
        present_new_fields = [col for col in df.columns if col in new_fields]
        print(f'🎯 New field columns present: {present_new_fields}')
        
        # Show field completeness for new fields
        print('\n📈 Field Completeness for New Fields:')
        for field in new_fields:
            if field in df.columns:
                filled_count = df[field].notna().sum()
                non_empty_count = df[field].astype(str).str.strip().ne('').sum()
                completeness = (non_empty_count / len(df)) * 100
                print(f'  📊 {field}: {completeness:.1f}% ({non_empty_count}/{len(df)})')
            else:
                print(f'  ❌ {field}: Column not found')
    
    else:
        print('❌ No properties scraped')

if __name__ == "__main__":
    test_enhanced_fields()
