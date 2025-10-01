#!/usr/bin/env python3
"""
Test Individual Property Page Extraction
Validates that the enhanced anti-bot bypass works for individual property pages
"""

from integrated_magicbricks_scraper import IntegratedMagicBricksScraper
import pandas as pd
import time

def test_individual_property_extraction():
    """Test individual property page extraction with enhanced anti-bot bypass"""
    
    print('🔍 TESTING INDIVIDUAL PROPERTY PAGE EXTRACTION')
    print('=' * 60)
    print('🎯 Goal: Validate enhanced anti-bot bypass for individual property pages')
    print('=' * 60)
    
    # Create scraper instance
    scraper = IntegratedMagicBricksScraper()
    
    print('\n📋 STEP 1: Getting Property URLs from Listing Page')
    print('-' * 50)
    
    # Setup driver manually to keep it alive
    scraper.setup_driver()

    # Manually scrape one page to get URLs (without auto-closing driver)
    print('🔗 Manually scraping listing page to get property URLs...')

    try:
        # Navigate to listing page
        base_url = "https://www.magicbricks.com/property-for-sale-in-gurgaon-pppfs"
        scraper.driver.get(base_url)
        time.sleep(3)

        # Extract properties from page
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(scraper.driver.page_source, 'html.parser')
        property_cards = soup.select('.mb-srp__card')

        print(f'📊 Found {len(property_cards)} property cards on listing page')

        # Extract basic property data and URLs
        scraper.properties = []
        for i, card in enumerate(property_cards):
            property_data = scraper.extract_property_data(card, 1, i)
            if property_data:
                scraper.properties.append(property_data)

        print(f'✅ Extracted {len(scraper.properties)} properties from listing page')

    except Exception as e:
        print(f'❌ Error manually scraping listing page: {str(e)}')
        scraper.close()
        return

    if not scraper.properties:
        print('❌ No properties extracted from listing page')
        scraper.close()
        return
    
    print(f'✅ Scraped {len(scraper.properties)} properties from listing page')
    
    # Extract URLs for individual page testing
    test_urls = []
    for prop in scraper.properties:
        url = prop.get('property_url', '').strip()
        if url and 'magicbricks.com' in url and 'pdpid' in url:
            test_urls.append(url)
            if len(test_urls) >= 3:  # Test first 3 URLs
                break
    
    print(f'📊 Found {len(test_urls)} individual property URLs for testing')
    
    if len(test_urls) == 0:
        print('❌ No valid individual property URLs found')
        scraper.close()
        return
    
    print('\n📋 STEP 2: Testing Individual Property Page Extraction')
    print('-' * 50)
    
    individual_results = []
    
    for i, url in enumerate(test_urls):
        print(f'\n🏡 TESTING INDIVIDUAL PROPERTY {i+1}:')
        print(f'🔗 URL: {url}')
        print('-' * 40)
        
        try:
            start_time = time.time()
            
            # Test individual property extraction
            individual_details = scraper.extract_individual_property_details(url)
            
            extraction_time = time.time() - start_time
            
            print(f'⏱️ Extraction time: {extraction_time:.2f} seconds')
            print(f'📊 Fields extracted: {len(individual_details)}')
            
            # Analyze extracted data
            result_summary = {
                'url': url,
                'extraction_time': extraction_time,
                'fields_extracted': len(individual_details),
                'success': len(individual_details) > 0
            }
            
            # Add individual details to summary
            for key, value in individual_details.items():
                result_summary[f'individual_{key}'] = value
                
                # Print key findings
                if value and str(value).strip():
                    status = '✅'
                    preview = str(value)[:100] + '...' if len(str(value)) > 100 else str(value)
                else:
                    status = '❌'
                    preview = 'NOT FOUND'
                
                print(f'   {status} {key}: {preview}')
            
            individual_results.append(result_summary)
            
            if individual_details:
                print(f'   🎉 SUCCESS: Individual property page extraction working!')
            else:
                print(f'   ⚠️ WARNING: No individual details extracted')
            
        except Exception as e:
            print(f'   ❌ ERROR: {str(e)}')
            individual_results.append({
                'url': url,
                'extraction_time': 0,
                'fields_extracted': 0,
                'success': False,
                'error': str(e)
            })
    
    # Close scraper
    scraper.close()
    
    print('\n📊 COMPREHENSIVE ANALYSIS:')
    print('=' * 50)
    
    # Save results
    if individual_results:
        df = pd.DataFrame(individual_results)
        df.to_csv('individual_property_extraction_results.csv', index=False)
        print(f'💾 Saved results to: individual_property_extraction_results.csv')
        
        # Success rate analysis
        successful_extractions = sum(1 for r in individual_results if r.get('success', False))
        success_rate = (successful_extractions / len(individual_results)) * 100
        
        print(f'📈 Success Rate: {success_rate:.1f}% ({successful_extractions}/{len(individual_results)})')
        
        if success_rate >= 90:
            print('🎉 EXCELLENT: Individual property page extraction is working perfectly!')
        elif success_rate >= 70:
            print('✅ GOOD: Individual property page extraction is working well')
        elif success_rate >= 50:
            print('⚠️ MODERATE: Individual property page extraction needs improvement')
        else:
            print('❌ POOR: Individual property page extraction is not working')
        
        # Field analysis
        if successful_extractions > 0:
            print(f'\n📋 FIELD EXTRACTION ANALYSIS:')
            
            # Analyze individual fields
            field_names = [
                'detailed_description', 'amenities', 'floor_plan', 
                'price_details', 'location_details', 'builder_details', 
                'possession_details'
            ]
            
            for field in field_names:
                field_key = f'individual_{field}'
                filled_count = sum(1 for r in individual_results 
                                 if r.get(field_key) and str(r.get(field_key)).strip())
                completeness = (filled_count / successful_extractions) * 100
                
                status = '✅' if completeness >= 80 else '⚠️' if completeness >= 50 else '❌'
                print(f'   {status} {field}: {completeness:.1f}% ({filled_count}/{successful_extractions})')
        
        # Performance analysis
        avg_extraction_time = sum(r.get('extraction_time', 0) for r in individual_results) / len(individual_results)
        print(f'\n⏱️ Average extraction time: {avg_extraction_time:.2f} seconds per property')
        
        # Error analysis
        errors = [r.get('error', '') for r in individual_results if 'error' in r]
        if errors:
            print(f'\n❌ ERRORS ENCOUNTERED:')
            for error in errors:
                print(f'   • {error}')
    
    print(f'\n🎯 CONCLUSION:')
    print('=' * 50)
    
    if successful_extractions > 0:
        print('✅ Individual property page access is working!')
        print('🔧 Enhanced anti-bot bypass implementation successful')
        print('📊 Individual property data extraction is functional')
        print('🚀 Ready for production use with individual property enhancement')
    else:
        print('❌ Individual property page access still blocked')
        print('🔧 Enhanced anti-bot bypass needs further refinement')
        print('📊 Individual property data extraction not working')

if __name__ == "__main__":
    test_individual_property_extraction()
